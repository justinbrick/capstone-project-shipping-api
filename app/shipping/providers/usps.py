"""
This module contains the USPS implementation of a shipment provider.
"""

__author__ = "Justin B. (justin@justin.directory)"

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
        self.price_mult = 1
        pass

    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        return await super().get_shipment_status(tracking_identifier)

    def create_random_id(self, associated: UUID) -> str:
        random_numbers = [
            ''.join(random.choices('0123456789', k=4))
            for _ in range(5)
        ]
        tracking_number = ' '.join(random_numbers)
        return tracking_number


client = USPSShipmentProvider()
