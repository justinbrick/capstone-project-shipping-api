"""
This module contains the UPS implementation of a shipment provider.
"""

__author__ = "Justin B. (justin@justin.directory)"


from uuid import UUID
from app.shipping.enums import Provider
from app.shipping.providers import ShipmentProvider
from app.shipping.models import CreateShipmentRequest, Shipment, ShipmentStatus
from datetime import datetime
import random


class UPSShipmentProvider(ShipmentProvider):
    """
    The UPS implementation of a shipment provider.
    """

    def __init__(self) -> None:
        self.provider_type = Provider.UPS
        self.speed_mult = 2.0
        pass

    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        return await super().get_shipment_status(tracking_identifier)

    def create_random_id(self, associated: UUID) -> str:
        random_id = ''.join(random.choices('0123456789ABCDEF', k=6))
        random_digits = ''.join(random.choices('0123456789', k=8))
        # 3E for economy
        return f"1Z{random_id}3E{random_digits}"


client = UPSShipmentProvider()
