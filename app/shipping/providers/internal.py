"""
This module contains the internal implementation of a shipment provider.
"""

__author__ = "Justin B. (justin@justin.directory)"


from uuid import UUID

from app.shipping.enums import Provider
from app.shipping.models import ShipmentStatus
from app.shipping.providers import ShipmentProvider


class InternalShipmentProvider(ShipmentProvider):
    """
    The internal implementation of a shipment provider.
    """

    def __init__(self) -> None:
        self.provider_type = Provider.INTERNAL
        self.speed_mult = 0.5
        self.price_mult = 0.8

    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        return await super().get_shipment_status(tracking_identifier)

    def create_random_id(self, associated: UUID) -> str:
        return str(associated)


client = InternalShipmentProvider()
