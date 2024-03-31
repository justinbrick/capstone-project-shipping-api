"""
Business logic regarding the delivery of shipments.
"""

from .enums import Provider
from .providers import ShipmentProvider
from .providers.fedex import client as fedex_client
from .providers.internal import client as internal_client
from .providers.ups import client as ups_client
from .providers.usps import client as usps_client


available_providers: dict[Provider, ShipmentProvider] = {
    Provider.FEDEX: fedex_client,
    Provider.UPS: ups_client,
    Provider.USPS: usps_client,
    Provider.INTERNAL: internal_client
}
