"""
In order to store models, they must be created using the declarative base in SQLAlchemy.
This base class is used to create the tables and metadata for the database.
All models must inherit from this base class, or it won't be created.
"""

__author__ = "Justin B. (justin@justin.directory)"

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import UUID as NativeUUID
from sqlalchemy import VARCHAR, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.shipping.enums import SLA
from app.shipping.models import Provider, Status


class Base(DeclarativeBase):
    """
    A base class used to create the tables and metadata for the database.
    """


class Order(Base):
    """
    Represents an order that has been placed.
    """
    __tablename__ = "orders"
    order_id: Mapped[UUID] = mapped_column(primary_key=True)
    """The ID of the order."""
    customer_id: Mapped[UUID]
    """The ID of the customer that placed the order."""
    created_at: Mapped[datetime]
    """The date and time that the order was created."""
    deliveries: Mapped[list["Delivery"]] = relationship(back_populates="order")


class Shipment(Base):
    """
    The shipment model represents a shipment that has been created for a specific order.
    Multiple shipments can be created for one order.
    """
    __tablename__ = "shipments"
    shipment_id: Mapped[UUID] = mapped_column(NativeUUID, primary_key=True)
    """The ID of the shipment. This is a primary key"""
    from_address: Mapped[str] = mapped_column(VARCHAR(255))
    """Where the shipment is coming from."""
    shipping_address: Mapped[str] = mapped_column(VARCHAR(255))
    """Where the shipment is going."""
    provider: Mapped[Provider]
    """The provider that is handling the shipment."""
    provider_shipment_id: Mapped[str] = mapped_column(VARCHAR(100))
    """The ID of the shipment that the provider uses."""
    created_at: Mapped[datetime]
    """The date and time that the shipment was created."""
    items: Mapped[list["ShipmentItem"]] = relationship()
    """The items that are associated with the shipment."""
    status: Mapped["ShipmentStatus"] = relationship()
    """The status of the shipment."""
    delivery: Mapped[Optional["Delivery"]] = relationship(
        secondary="shipment_delivery_info",
        back_populates="shipments"
    )
    """The delivery that is associated with the shipment."""
    reservation: Mapped[Optional["ShippingEmployeeReservation"]
                        ] = relationship()


class ShipmentDeliveryInfo(Base):
    """
    A mapping of a shipment to it's delivery.
    """
    __tablename__ = "shipment_delivery_info"
    shipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("shipments.shipment_id"), primary_key=True)
    """A shipment ID that is associated with the delivery."""
    delivery_id: Mapped[UUID] = mapped_column(
        ForeignKey("deliveries.delivery_id"), primary_key=True)
    """A delivery ID that is associated with the shipment."""


class Delivery(Base):
    """
    Represents a full delivery, composed of the individual orders.
    """
    __tablename__ = "deliveries"
    delivery_id: Mapped[UUID] = mapped_column(NativeUUID, primary_key=True)
    """The ID of the delivery."""
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.order_id"))
    """The ID of the order that is associated with the delivery."""
    order: Mapped[Order] = relationship(back_populates="deliveries")
    """The order that is associated with the delivery."""
    recipient_address: Mapped[str] = mapped_column(VARCHAR(255))
    """The address that the delivery is going to."""
    created_at: Mapped[datetime]
    """The date and time that the delivery was created."""
    fulfilled_at: Mapped[datetime] = mapped_column(nullable=True)
    """The date and time that the delivery was fulfilled."""
    delivery_sla: Mapped[SLA]
    """The service level agreement that the delivery is under."""
    shipments: Mapped[list[Shipment]] = relationship(
        secondary="shipment_delivery_info",
        back_populates="delivery"
    )
    """The shipments that are associated with the delivery."""


class WarehouseItem(Base):
    """
    An item that is stored in a warehouse.
    """
    __tablename__ = "warehouse_items"
    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("warehouses.warehouse_id"), primary_key=True)
    upc: Mapped[int] = mapped_column(primary_key=True)
    stock: Mapped[int]


class Return(Base):
    """
    Represents a return for a given order.
    """
    __tablename__ = "returns"
    return_id: Mapped[UUID] = mapped_column(NativeUUID, primary_key=True)
    """
    The ID of the return.
    """
    shipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("shipments.shipment_id"))
    """
    The ID of the associated shipment that is used to get a return package.
    """
    order_id: Mapped[UUID] = mapped_column(NativeUUID)
    """
    The ID of the order that is associated with the return.
    """
    created_at: Mapped[datetime]
    """
    The date and time that the return was created.
    """
    shipment: Mapped[Shipment] = relationship()
    """
    The shipment that is associated with the return.
    """


class ShipmentItem(Base):
    """
    A shipment item that is related to a given shipment.
    There can be multiple items associated with one shipment.
    """
    __tablename__ = "shipment_items"
    shipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("shipments.shipment_id"), primary_key=True)  # potential needed? native_uuid
    """The ID of the shipment that this item is associated with."""
    upc: Mapped[int] = mapped_column(primary_key=True)
    """The UPC of the item."""
    stock: Mapped[int]
    """The amount requested for this item."""


class ShipmentStatus(Base):
    """
    The status of any given shipment.
    For internal purposes only.
    """
    __tablename__ = "shipment_status"
    shipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("shipments.shipment_id"), primary_key=True
    )
    """The ID of the shipment that this status is associated with."""
    message: Mapped[Status]
    """The status of the shipment."""
    expected_at: Mapped[datetime]
    """The expected time that the shipment should be delivered."""
    updated_at: Mapped[datetime]
    """The last time that the status was updated."""
    delivered_at: Mapped[Optional[datetime]]
    """The time that the shipment was delivered, or None if not delivered."""


class Warehouse(Base):
    """
    A warehouse that is used to store items and fulfill orders.
    """
    __tablename__ = "warehouses"
    warehouse_id: Mapped[UUID] = mapped_column(NativeUUID, primary_key=True)
    """The ID of the warehouse."""
    address: Mapped[str] = mapped_column(VARCHAR(255))
    """The address of the warehouse."""
    latitude: Mapped[float]
    """The latitude of the warehouse."""
    longitude: Mapped[float]
    """The longitude of the warehouse."""
    items: Mapped[list["WarehouseItem"]] = relationship()
    """The items that are stored in the warehouse."""


class ShippingEmployeeReservation(Base):
    """
    An employee reservation represents a reservation for a given employee to handle a shipment.
    """
    __tablename__ = "shipping_employee_reservations"
    employee_id: Mapped[UUID] = mapped_column(NativeUUID, primary_key=True)
    """The ID of the employee that is reserved for the shipment."""
    shipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("shipments.shipment_id")
    )
    """The ID of the shipment that the employee is reserved for."""
