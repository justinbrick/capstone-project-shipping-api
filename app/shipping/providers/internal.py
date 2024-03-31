"""
This module contains the internal implementation of a shipment provider.
"""

from app.shipping.providers import ShipmentProvider
from app.shipping.models import Shipment, ShipmentStatus
from datetime import datetime


class InternalShipmentProvider(ShipmentProvider):
    """
    The internal implementation of a shipment provider.
    """

    def __init__(self) -> None:
        pass

    async def create_shipment(self, request: dict) -> Shipment:
        return await super().create_shipment(request)

    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        return await super().get_shipment_status(tracking_identifier)

    async def get_estimated_delivery_date(self, from_address: str, to_address: str) -> datetime:
        return await super().get_estimated_delivery_date(from_address, to_address)

    async def get_shipment_location(self, tracking_identifier: str) -> str | None:
        return f"Package {tracking_identifier} is in North Carolina."


client = InternalShipmentProvider()
