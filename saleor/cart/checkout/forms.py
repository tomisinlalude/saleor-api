from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import pgettext_lazy

from ...cart.models import Cart
from ...core.utils import format_money
from ...core.utils.taxes import display_gross_prices
from ...checkout.forms import CheckoutAddressField
from ...shipping.models import ShippingMethodCountry
from ...shipping.utils import get_taxed_shipping_price


class AnonymousUserShippingForm(forms.Form):
    """Additional shipping information form for users who are not logged in."""

    email = forms.EmailField(
        required=True, widget=forms.EmailInput(
            attrs={'autocomplete': 'shipping email'}),
        label=pgettext_lazy('Shipping form field label', 'Email'))


class AddressChoiceForm(forms.Form):
    """Choose one of user's addresses or to create new one."""

    NEW_ADDRESS = 'new_address'
    CHOICES = [
        (NEW_ADDRESS, pgettext_lazy(
            'Shipping addresses form choice', 'Enter a new address'))]

    address = CheckoutAddressField(
        label=pgettext_lazy('Shipping addresses form field label', 'Address'),
        choices=CHOICES, initial=NEW_ADDRESS)

    def __init__(self, *args, **kwargs):
        addresses = kwargs.pop('addresses')
        super().__init__(*args, **kwargs)
        address_choices = [(address.id, str(address)) for address in addresses]
        self.fields['address'].choices = self.CHOICES + address_choices


# FIXME: why is this called a country choice field?
class ShippingCountryChoiceField(forms.ModelChoiceField):
    """Shipping method country choice field.

    Uses a radio group instead of a dropdown and includes estimated shipping
    prices.
    """
    taxes = None
    widget = forms.RadioSelect()

    def label_from_instance(self, obj):
        """Return a friendly label for the shipping method."""
        price = get_taxed_shipping_price(obj.price, self.taxes)
        if display_gross_prices():
            price = price.gross
        else:
            price = price.net
        price_html = format_money(price)
        label = mark_safe('%s %s' % (obj.shipping_method, price_html))
        return label


class CartShippingMethodForm(forms.ModelForm):
    """Cart shipping method form."""

    shipping_method = ShippingCountryChoiceField(
        queryset=ShippingMethodCountry.objects.select_related(
            'shipping_method').order_by('price').all(),
        label=pgettext_lazy(
            'Shipping method form field label', 'Shipping method'),
        required=True)

    class Meta:
        model = Cart
        fields = ['shipping_method']

    def __init__(self, *args, **kwargs):
        taxes = kwargs.pop('taxes')
        super().__init__(*args, **kwargs)
        method_field = self.fields['shipping_method']
        method_field.taxes = taxes

        country_code = self.instance.shipping_address.country.code
        if country_code:
            queryset = method_field.queryset
            method_field.queryset = queryset.unique_for_country_code(
                country_code)

        if self.initial.get('shipping_method') is None:
            self.initial['shipping_method'] = method_field.queryset.first()

        method_field.empty_label = None
