import graphene
from django.utils.text import slugify

from ....channel.error_codes import ChannelErrorCode
from ...tests.utils import assert_no_permission, get_graphql_content

CHANNEL_UPDATE_MUTATION = """
    mutation UpdateChannel($id: ID!,$input: ChannelUpdateInput!){
        channelUpdate(id: $id, input: $input){
            channel{
                id
                name
                slug
                currencyCode
                shippingZones{
                    id
                }
            }
            channelErrors{
                field
                code
                message
                shippingZones
            }
        }
    }
"""


def test_channel_update_mutation_as_staff_user(
    permission_manage_channels, staff_api_client, channel_USD
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = "new_slug"
    variables = {"id": channel_id, "input": {"name": name, "slug": slug}}

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelUpdate"]
    assert not data["channelErrors"]
    channel_data = data["channel"]
    channel_USD.refresh_from_db()
    assert channel_data["name"] == channel_USD.name == name
    assert channel_data["slug"] == channel_USD.slug == slug
    assert channel_data["currencyCode"] == channel_USD.currency_code == "USD"


def test_channel_update_mutation_as_app(
    permission_manage_channels, app_api_client, channel_USD
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = "new_slug"
    variables = {"id": channel_id, "input": {"name": name, "slug": slug}}

    # when
    response = app_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelUpdate"]
    assert not data["channelErrors"]
    channel_data = data["channel"]
    channel_USD.refresh_from_db()
    assert channel_data["name"] == channel_USD.name == name
    assert channel_data["slug"] == channel_USD.slug == slug
    assert channel_data["currencyCode"] == channel_USD.currency_code == "USD"


def test_channel_update_mutation_as_customer(user_api_client, channel_USD):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = "new_slug"
    variables = {"id": channel_id, "input": {"name": name, "slug": slug}}

    # when
    response = user_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(),
    )

    # then
    assert_no_permission(response)


def test_channel_update_mutation_as_anonymous(api_client, channel_USD):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = "new_slug"
    variables = {"id": channel_id, "input": {"name": name, "slug": slug}}

    # when
    response = api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(),
    )

    # then
    assert_no_permission(response)


def test_channel_update_mutation_slugify_slug_field(
    permission_manage_channels, staff_api_client, channel_USD
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "testName"
    slug = "Invalid slug"
    variables = {"id": channel_id, "input": {"name": name, "slug": slug}}

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    channel_data = content["data"]["channelUpdate"]["channel"]
    assert channel_data["slug"] == slugify(slug)


def test_channel_update_mutation_with_duplicated_slug(
    permission_manage_channels, staff_api_client, channel_USD, channel_PLN
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "New Channel"
    slug = channel_PLN.slug
    variables = {"id": channel_id, "input": {"name": name, "slug": slug}}

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    error = content["data"]["channelUpdate"]["channelErrors"][0]
    assert error["field"] == "slug"
    assert error["code"] == ChannelErrorCode.UNIQUE.name


def test_channel_update_mutation_only_name(
    permission_manage_channels, staff_api_client, channel_USD
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = channel_USD.slug
    variables = {"id": channel_id, "input": {"name": name}}

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelUpdate"]
    assert not data["channelErrors"]
    channel_data = data["channel"]
    channel_USD.refresh_from_db()
    assert channel_data["name"] == channel_USD.name == name
    assert channel_data["slug"] == channel_USD.slug == slug
    assert channel_data["currencyCode"] == channel_USD.currency_code == "USD"


def test_channel_update_mutation_only_slug(
    permission_manage_channels, staff_api_client, channel_USD
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = channel_USD.name
    slug = "new_slug"
    variables = {"id": channel_id, "input": {"slug": slug}}

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelUpdate"]
    assert not data["channelErrors"]
    channel_data = data["channel"]
    channel_USD.refresh_from_db()
    assert channel_data["name"] == channel_USD.name == name
    assert channel_data["slug"] == channel_USD.slug == slug
    assert channel_data["currencyCode"] == channel_USD.currency_code == "USD"


def test_channel_update_mutation_add_shipping_zone(
    permission_manage_channels, staff_api_client, channel_USD, shipping_zone
):
    # given
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = "new_slug"
    shipping_zone_id = graphene.Node.to_global_id("ShippingZone", shipping_zone.pk)
    variables = {
        "id": channel_id,
        "input": {"name": name, "slug": slug, "addShippingZones": [shipping_zone_id]},
    }

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelUpdate"]
    assert not data["channelErrors"]
    channel_data = data["channel"]
    channel_USD.refresh_from_db()
    assert channel_data["name"] == channel_USD.name == name
    assert channel_data["slug"] == channel_USD.slug == slug
    assert channel_data["currencyCode"] == channel_USD.currency_code == "USD"
    assert [zone["id"] for zone in channel_data["shippingZones"]] == [shipping_zone_id]


def test_channel_update_mutation_remove_shipping_zone(
    permission_manage_channels, staff_api_client, channel_USD, shipping_zones
):
    # given
    channel_USD.shipping_zones.add(*shipping_zones)

    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = "new_slug"
    shipping_zone = shipping_zones[0].pk
    remove_shipping_zone = graphene.Node.to_global_id("ShippingZone", shipping_zone)
    variables = {
        "id": channel_id,
        "input": {
            "name": name,
            "slug": slug,
            "removeShippingZones": [remove_shipping_zone],
        },
    }
    assert channel_USD.shipping_method_listings.filter(
        shipping_method__shipping_zone=shipping_zone
    )

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelUpdate"]
    assert not data["channelErrors"]
    channel_data = data["channel"]
    channel_USD.refresh_from_db()
    assert channel_data["name"] == channel_USD.name == name
    assert channel_data["slug"] == channel_USD.slug == slug
    assert channel_data["currencyCode"] == channel_USD.currency_code == "USD"
    zones = [zone["id"] for zone in channel_data["shippingZones"]]
    assert len(zones) == len(shipping_zones) - 1
    assert remove_shipping_zone not in zones
    assert not channel_USD.shipping_method_listings.filter(
        shipping_method__shipping_zone=shipping_zone
    )


def test_channel_update_mutation_add_and_remove_shipping_zone(
    permission_manage_channels,
    staff_api_client,
    channel_USD,
    shipping_zones,
    shipping_zone,
):
    # given
    channel_USD.shipping_zones.add(*shipping_zones)
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = "new_slug"
    remove_shipping_zone = graphene.Node.to_global_id(
        "ShippingZone", shipping_zones[0].pk
    )
    add_shipping_zone = graphene.Node.to_global_id("ShippingZone", shipping_zone.pk)
    variables = {
        "id": channel_id,
        "input": {
            "name": name,
            "slug": slug,
            "addShippingZones": [add_shipping_zone],
            "removeShippingZones": [remove_shipping_zone],
        },
    }

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelUpdate"]
    assert not data["channelErrors"]
    channel_data = data["channel"]
    channel_USD.refresh_from_db()
    assert channel_data["name"] == channel_USD.name == name
    assert channel_data["slug"] == channel_USD.slug == slug
    assert channel_data["currencyCode"] == channel_USD.currency_code == "USD"
    zones = [zone["id"] for zone in channel_data["shippingZones"]]
    assert len(zones) == len(shipping_zones)
    assert remove_shipping_zone not in zones
    assert add_shipping_zone in zones


def test_channel_update_mutation_duplicated_shipping_zone(
    permission_manage_channels,
    staff_api_client,
    channel_USD,
    shipping_zones,
    shipping_zone,
):
    # given
    channel_USD.shipping_zones.add(*shipping_zones)
    channel_id = graphene.Node.to_global_id("Channel", channel_USD.id)
    name = "newName"
    slug = "new_slug"
    remove_shipping_zone = graphene.Node.to_global_id(
        "ShippingZone", shipping_zones[0].pk
    )
    add_shipping_zone = graphene.Node.to_global_id("ShippingZone", shipping_zone.pk)
    variables = {
        "id": channel_id,
        "input": {
            "name": name,
            "slug": slug,
            "addShippingZones": [add_shipping_zone],
            "removeShippingZones": [remove_shipping_zone, add_shipping_zone],
        },
    }

    # when
    response = staff_api_client.post_graphql(
        CHANNEL_UPDATE_MUTATION,
        variables=variables,
        permissions=(permission_manage_channels,),
    )
    content = get_graphql_content(response)

    # then
    data = content["data"]["channelUpdate"]
    assert not data["channel"]
    errors = data["channelErrors"]
    assert len(errors) == 1
    assert errors[0]["field"] == "shippingZones"
    assert errors[0]["code"] == ChannelErrorCode.DUPLICATED_INPUT_ITEM.name
    assert errors[0]["shippingZones"] == [add_shipping_zone]
