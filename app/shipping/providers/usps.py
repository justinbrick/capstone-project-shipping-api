"""
This module contains the USPS implementation of a shipment provider.
"""

from app.shipping.enums import Provider
from app.shipping.providers import ShipmentProvider
from app.shipping.models import CreateShipmentRequest, Shipment, ShipmentStatus
from datetime import datetime


class USPSShipmentProvider(ShipmentProvider):
    def __init__(self) -> None:
        self.provider_type = Provider.USPS
        pass

    async def create_shipment(self, request: CreateShipmentRequest) -> Shipment:
        return await super().create_shipment(request)

    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        return await super().get_shipment_status(tracking_identifier)

    async def get_shipment_location(self, tracking_identifier: str) -> str | None:
        return f"Package {tracking_identifier} is in North Carolina."


client = USPSShipmentProvider()
