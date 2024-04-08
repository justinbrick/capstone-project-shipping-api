"""
This module contains the USPS implementation of a shipment provider.
"""

import random
from uuid import UUID
from app.shipping.enums import Provider
from app.shipping.providers import ShipmentProvider
from app.shipping.models import CreateShipmentRequest, Shipment, ShipmentStatus
from datetime import datetime


class USPSShipmentProvider(ShipmentProvider):
    def __init__(self) -> None:
        self.provider_type = Provider.USPS
        self.speed_mult = 2.5
        pass

    async def create_shipment(self, request: CreateShipmentRequest) -> Shipment:
        return await super().create_shipment(request)

    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        return await super().get_shipment_status(tracking_identifier)

    def create_random_id(self, associated: UUID) -> str:
        # TODO: Needs true usps tracking number
        random_id = ''.join(random.choices('0123456789ABCDEF', k=6))
        random_digits = ''.join(random.choices('0123456789', k=8))
        # 3E for economy
        return f"1Z{random_id}3E{random_digits}"

    async def get_shipment_location(self, tracking_identifier: str) -> str | None:
        return f"Package {tracking_identifier} is in North Carolina."


client = USPSShipmentProvider()
