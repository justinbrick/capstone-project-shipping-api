"""
Mock FedEx tracking API
"""

__author__ = "Justin B. (justin@justin.directory)"

import random
from uuid import UUID

from app.shipping.enums import Provider
from . import ShipmentProvider
from ..models import ShipmentStatus

"""
TODO: Implement the following functions to complete the FedEx mock API.

1. Mock Database to hold mock tracking numbers and hard coded statuses(FINISHED)

2. Add a tracking number to the database when a tracking number is generated(FINISHED)

3. Implement get_status and get_location functions to return the status and location of a package with a given tracking number(FINISHED)

4. Speed multiplier/cost multiplier for shipment price estimates.(FINISHED)

5. Implement users.py router to query user information whether previous or current(sort by date descending) shipments have been delivered or are in transit.(FINISHED)

"""


class FedexShipmentProvider(ShipmentProvider):
    """
    The Fedex implementation of a shipment provider.
    """

    def __init__(self) -> None:
        self.provider_type = Provider.FEDEX
        self.speed_mult = 1.5
        self.price_mult = 1.25

    def create_random_id(self, associated: UUID) -> str:
        random_numbers = [
            ''.join(random.choices('0123456789', k=4))
            for _ in range(3)
        ]
        tracking_number = ' '.join(random_numbers)
        return tracking_number

    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        return await super().get_shipment_status(tracking_identifier)


client = FedexShipmentProvider()
