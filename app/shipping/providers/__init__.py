"""
A module containing all of the different providers and their client implementations.
"""


from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from geopy.distance import geodesic

from app.shipping.enums import Provider, Status
from ..models import Shipment, ShipmentStatus, CreateShipmentRequest
from app.shipping.location import get_address_coordinates


class ShipmentProvider(ABC):
    """
    A shipment provider which can be used to interact with shipping services in a normalized way.
    """

    provider_type: Provider
    """The type of provider that this client is for."""
    speed_mult: float
    """The speed multiplier for the provider - used to approximate delivery times."""

    @abstractmethod
    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        """
        Get the status of a shipment using a tracking identifier.
        :param tracking_identifier: the tracking identifier to get the status for
        :return: the status of the shipment
        """
        raise NotImplementedError()

    async def get_shipment_location(self, tracking_identifier: str) -> str | None:
        """
        Get the location of a shipment using a tracking identifier.
        :param tracking_identifier: the tracking identifier to get the location for
        :return: the location of the shipment
        """
        return None

    async def create_shipment(self, request: CreateShipmentRequest) -> Shipment:
        """
        Create a shipment using the request.
        :param request: the request to create the shipment
        :return: the created shipment
        """
        shipment_id = uuid4()
        created_at = datetime.now()
        expected_time = await self.get_delivery_time(request.from_address, request.shipping_address)
        expected_at = created_at + expected_time

        shipment = Shipment(
            shipment_id=shipment_id,
            shipping_address=request.shipping_address,
            from_address=request.from_address,
            provider=self.provider_type,
            provider_shipment_id=self.create_random_id(shipment_id),
            created_at=created_at,
            items=request.items,
            status=ShipmentStatus(
                shipment_id=shipment_id,
                expected_at=expected_at,
                updated_at=created_at,
                message=Status.PENDING
            )
        )

        return shipment

    @abstractmethod
    def create_random_id(self, associated: UUID) -> str:
        """
        Create a random shipment ID relevant to the provider.
        If the provider is internal, it will return the associated ID instead.

        :param associated: the associated ID in our database.
        :return: a random shipment ID
        """
        raise NotImplementedError()

    async def get_delivery_time(self, to_address: str, from_address: str) -> timedelta:
        """
        Get the delivery time from one address to another.

        :param to_address: the address to ship to
        :param from_address: the address to ship from
        :return: the delivery time
        """

        to_coords = await get_address_coordinates(to_address)
        from_coords = await get_address_coordinates(from_address)
        dist = geodesic(to_coords, from_coords).miles
        # Default of 12 hours per 100 miles
        # Times by the speed multiplier
        time_hours = (dist / 100 * 12) * self.speed_mult
        return timedelta(hours=time_hours)
