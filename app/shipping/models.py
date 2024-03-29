"""
Models for the shipping API.
"""

from .enums import Provider, Status

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class ShipmentItem(BaseModel):
    """
    A shipment item that is related to a given shipment.
    There can be multiple items associated with one shipment.
    """
    upc: int
    stock: int


class Shipment(BaseModel):
    """
    The shipment model represents a shipment that has been created for a specific order.
    Multiple shipments can be created for one order.
    """
    order_id: UUID
    shipment_id: UUID
    shipping_address: str
    provider: Provider
    provider_shipment_id: str
    created_at: datetime

    model_config = {
        # This is a flag to indicate that the model should be created from the attributes.
        # Used to work with ORM models.
        "from_attributes": True
    }


class CreateShipmentRequest(BaseModel):
    """
    The shipment request model represents a request to create a shipment regarding a specific order.
    This is not stored in any database and is rather just used so that we can create the shipment itself.
    """
    order_id: UUID
    shipping_address: str
    provider: Provider


class ShipmentStatus(BaseModel):
    """
    The status of a shipment
    Due to varying sources of shipment delivery, this must be put into one unified response.
    """
    order_id: UUID
    status: Status
