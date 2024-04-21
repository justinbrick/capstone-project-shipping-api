"""
A module containing all of the different providers and their client implementations.
"""

__author__ = "Justin B. (justin@justin.directory)"

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from geopy.distance import geodesic

from app.shipping.enums import Provider, Status
from app.shipping.location import get_address_coordinates

from ..models import CreateShipmentRequest, Shipment, ShipmentStatus


class ShipmentProvider(ABC):
    """
    A shipment provider which can be used to interact with shipping services in a normalized way.
    """

    provider_type: Provider
    """The type of provider that this client is for."""
    speed_mult: float
    """The speed multiplier for the provider - used to approximate delivery times."""
    price_mult: float
    """The price multiplier for the provider - used to approximate shipping costs."""

    @abstractmethod
    async def get_shipment_status(self, tracking_identifier: str) -> ShipmentStatus:
        """
        Get the status of a shipment using a tracking identifier.
        :param tracking_identifier: the tracking identifier to get the status for
        :return: the status of the shipment
        """

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

    async def get_shipment_price(self, to_address: str, from_address: str) -> float:
        """
        Get the price of shipping from one address to another.

        :param to_address: the address to ship to
        :param from_address: the address to ship from
        :return: the price of shipping
        """

        to_coords = await get_address_coordinates(to_address)
        from_coords = await get_address_coordinates(from_address)
        dist = geodesic(to_coords, from_coords).miles
        # Default of $5 per 100 miles
        # Times by the price multiplier
        price = (dist / 100 * 5) * self.price_mult

        return price


async def get_current_delivery_progress_estimate(shipment: Shipment) -> float:
    """
    Get the current delivery progress of a shipment.
    :param shipment: the shipment to get the progress for
    :return: the current delivery progress
    """
    if shipment.status.message == Status.DELIVERED:
        return 1.0
    elif shipment.status.message == Status.PENDING:
        return 0.0
    else:
        elapsed = datetime.now() - shipment.created_at
        expected = shipment.status.expected_at - shipment.created_at
        return elapsed / expected


async def get_delivery_distance_away(shipment: Shipment) -> float:
    """
    Get the distance away from the destination of a shipment.
    :param shipment: the shipment to get the distance for
    :return: the distance away from the destination
    """
    if shipment.status.message == Status.DELIVERED:
        return 0.0
    elif shipment.status.message == Status.PENDING:
        return 1.0
    else:
        to_coords = await get_address_coordinates(shipment.shipping_address)
        from_coords = await get_address_coordinates(shipment.from_address)
        dist = geodesic(to_coords, from_coords).miles
