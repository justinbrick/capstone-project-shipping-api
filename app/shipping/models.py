"""
Models for the shipping API.
"""

from typing import Optional
from .enums import Provider, Status, SLA

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
    shipment_id: UUID
    shipping_address: str
    provider: Provider
    provider_shipment_id: str
    created_at: datetime
    delivered_at: Optional[datetime] = None

    model_config = {
        # This is a flag to indicate that the model should be created from the attributes.
        # Used to work with ORM models.
        "from_attributes": True
    }


class DeliveryShipment(Shipment):
    """
    A shipment that is created for a delivery.
    """
    delivery_id: UUID


class Delivery(BaseModel):
    """
    Represents a full delivery, composed of the individual orders.
    This is a simple composite model to represent all the orders that this is made of.
    """
    order_id: UUID
    created_at: datetime
    fulfilled_at: Optional[datetime] = None
    delivery_sla: SLA
    shipments: list[DeliveryShipment]


class DeliveryTimeResponse(BaseModel):
    """
    Represents the response with delivery time, items, stock, and the provider.
    """
    delivery_time: datetime
    items: list[ShipmentItem]
    provider: Provider


class ShipmentDeliveryBreakdown(BaseModel):
    """
    Provides a breakdown of the delivery times and shipping providers, given a specific order.
    """
    order_id: UUID
    recipient_address: str
    delivery_times: list[DeliveryTimeResponse]


class CreateDeliveryRequest(BaseModel):
    """
    A request to create a delivery.
    """
    delivery_sla: SLA


class CreateShipmentRequest(BaseModel):
    """
    The shipment request model represents a request to create a shipment regarding a specific order.
    This is not stored in any database and is rather just used so that we can create the shipment itself.
    """
    shipping_address: str
    items: list[ShipmentItem]
    provider: Provider


class CreateReturnRequest(BaseModel):
    """
    A request which represents a return for a specific order.
    """
    order_id: UUID
    items: list[ShipmentItem]


class ShipmentStatus(BaseModel):
    """
    The status of a shipment
    Due to varying sources of shipment delivery, this must be put into one unified response.
    """
    order_id: UUID
    status: Status
