"""
Mock FedEx tracking API
"""

from datetime import datetime, timedelta
from typing import Any, Coroutine
from uuid import UUID

from app.shipping.enums import Provider
from . import ShipmentProvider
from ..models import CreateShipmentRequest, Shipment, ShipmentStatus

"""
TODO: Implement the following functions to complete the FedEx mock API.

1. Mock Database to hold mock tracking numbers and hard coded statuses

2. Add a tracking number to the database when a tracking number is generated

3. Implement get_status and get_location functions to return the status and location of a package with a given tracking number

"""


class FedexShipmentProvider(ShipmentProvider):
    """
    The Fedex implementation of a shipment provider.
    """

    def __init__(self) -> None:
        self.provider_type = Provider.FEDEX
        self.speed_mult = 1.5

    def create_random_id(self, associated: UUID) -> str:
        # TODO: Needs true fedex tracking number
        return associated

    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        return await super().get_shipment_status(tracking_identifier)

    async def get_shipment_location(self, tracking_identifier: str) -> str | None:
        return f"Package {tracking_identifier} is in North Carolina."


client = FedexShipmentProvider()
