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
    """The UPC of the item."""
    stock: int
    """The amount requested for this item."""


class Shipment(BaseModel):
    """
    The shipment model represents a shipment that has been created for a specific order.
    Multiple shipments can be created for one order.
    """
    shipment_id: UUID
    """A unique identifier for the shipment."""
    from_address: str
    """The address that the shipment is coming from."""
    shipping_address: str
    """The address that the shipment is going to."""
    provider: Provider
    """The provider that is going to be used for this shipment."""
    provider_shipment_id: str
    """The ID that the provider has assigned to this shipment, for external references."""
    created_at: datetime
    """The time that this shipment was created."""
    expected_at: datetime
    """The time that this shipment is expected to be delivered."""
    delivered_at: Optional[datetime] = None
    """The time that this shipment was delivered."""
    items: list[ShipmentItem]
    """The items that are going to be shipped."""

    model_config = {
        # This is a flag to indicate that the model should be created from the attributes.
        # Used to work with ORM models.
        "from_attributes": True
    }


class Delivery(BaseModel):
    """
    Represents a full delivery, composed of the individual orders.
    This is a simple composite model to represent all the orders that this is made of.
    """
    delivery_id: UUID
    """The ID of the delivery."""
    order_id: UUID
    """The ID of the order that this delivery is associated with."""
    shipments: list[Shipment]
    """The shipments that are associated with this delivery."""
    created_at: datetime
    """The time that this delivery was created."""
    fulfilled_at: Optional[datetime] = None
    """The time that this delivery was fulfilled."""
    delivery_sla: SLA
    """The SLA that this delivery must adhere to."""


class Return(BaseModel):
    """
    Represents a return, which contains the order ID associated to the return,
    and a shipment which contains the items to be returned.
    """
    order_id: UUID
    """The ID of the order that this return is associated with."""
    return_id: UUID
    """The ID of the return."""
    shipment: Shipment
    """The shipment that contains the items to be returned."""


class DeliveryTimeResponse(BaseModel):
    """
    Represents the response with delivery time, items, stock, and the provider.
    """
    from_address: str
    """The address of the warehouse that the delivery is coming from."""
    delivery_time: datetime
    """The time that the delivery is expected to be delivered."""
    items: list[ShipmentItem]
    """The items that are going to be delivered."""
    provider: Provider
    """The provider that is going to deliver the items."""


class ShipmentDeliveryBreakdown(BaseModel):
    """
    Provides a breakdown of the delivery times and shipping providers, given a specific order.
    """
    recipient_address: str
    """The address that the delivery is going to."""
    expected_at: datetime
    """The time that the delivery is expected to be delivered."""
    can_meet_sla: bool
    """Whether or not the delivery can meet the SLA."""
    delivery_times: list[DeliveryTimeResponse]
    """A list of delivery providers and their respective delivery times, given a set of items."""


class CreateDeliveryRequest(BaseModel):
    """
    A request to create a delivery. A delivery is based under an order, and can have multiple shipments.
    """
    recipient_address: str
    """The address that the delivery is going to."""
    delivery_sla: SLA
    """The SLA that this delivery request must adhere to."""
    items: list[ShipmentItem]
    """A list of items that are going to be delivered."""


class CreateShipmentRequest(BaseModel):
    """
    The shipment request model represents a request to create a shipment regarding a specific order.
    Usually used for returns & internal shipments.
    """
    from_address: str
    """The address that the shipment is coming from."""
    shipping_address: str
    """The address that the shipment is going to."""
    items: list[ShipmentItem]
    """The items that are going to be shipped."""
    provider: Provider
    """The provider that is going to be used for this shipment."""


class CreateReturnRequest(BaseModel):
    """
    A request which represents a return for a specific order.
    """
    order_id: UUID
    """The ID of the order that this return request is associated with."""
    items: list[ShipmentItem]
    """The items in the order that are being returned."""
    from_address: str
    """The address that the return is coming from."""


class ShipmentStatus(BaseModel):
    """
    The status of a shipment
    Due to varying sources of shipment delivery, this must be put into one unified response.
    """
    order_id: UUID
    """The ID of the order that this shipment status is associated with."""
    status: Status
    """The status of the shipment."""
