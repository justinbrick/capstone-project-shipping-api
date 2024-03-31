"""
A module containing all of the different providers and their client implementations.
"""


from abc import ABC, abstractmethod
from datetime import datetime
from ..models import Shipment, ShipmentStatus, CreateShipmentRequest


class ShipmentProvider(ABC):
    """
    A shipment provider which can be used to interact with shipping services in a normalized way.
    """
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

    @abstractmethod
    async def create_shipment(self, request: CreateShipmentRequest) -> Shipment:
        """
        Create a shipment using the request.
        :param request: the request to create the shipment
        :return: the created shipment
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_estimated_delivery_date(self, from_address: str, to_address: str) -> datetime:
        """
        Get the expected delivery date from one address to a second address.
        :param from_address: the address to ship from
        :param to_address: the address to ship to
        :return: the expected delivery date
        """
        raise NotImplementedError()
