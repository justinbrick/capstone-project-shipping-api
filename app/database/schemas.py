"""
In order to store models, they must be created using the declarative base in SQLAlchemy.
This base class is used to create the tables and metadata for the database.
All models must inherit from this base class, or it won't be created.
"""

from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ..shipping.models import Provider, Status


class Base(DeclarativeBase):
    """
    A base class used to create the tables and metadata for the database.
    """


class Shipment(Base):
    """
    The shipment model represents a shipment that has been created for a specific order.
    Multiple shipments can be created for one order.
    """
    __tablename__ = "shipments"
    shipment_id: Mapped[UUID] = mapped_column(primary_key=True)
    shipping_address: Mapped[str] = mapped_column(VARCHAR(255))
    provider: Mapped[Provider]
    provider_shipment_id: Mapped[str] = mapped_column(VARCHAR(100))
    created_at: Mapped[datetime]
    expected_at: Mapped[datetime]
    items: Mapped[list["ShipmentItem"]] = relationship()


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
    delivery_id: Mapped[UUID] = mapped_column(primary_key=True)
    """
    The ID of the delivery.
    """
    order_id: Mapped[UUID]
    """
    The ID of the order that is associated with the delivery.
    """
    created_at: Mapped[datetime]
    """
    The date and time that the delivery was created.
    """
    fulfilled_at: Mapped[datetime] = mapped_column(nullable=True)
    """
    The date and time that the delivery was fulfilled.
    """
    delivery_sla: Mapped[str] = mapped_column(VARCHAR(100))
    """
    The service level agreement that the delivery is under.
    """
    delivery_shipments: Mapped[list["ShipmentDeliveryInfo"]] = relationship()
    """
    The shipments that are associated with the delivery.
    """


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
    return_id: Mapped[UUID] = mapped_column(primary_key=True)
    """
    The ID of the return.
    """
    shipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("shipments.shipment_id"))
    """
    The ID of the associated shipment that is used to get a return package.
    """
    order_id: Mapped[UUID]
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
        ForeignKey("shipments.shipment_id"), primary_key=True)
    upc: Mapped[int] = mapped_column(primary_key=True)
    stock: Mapped[int]


class ShipmentStatus(Base):
    """
    The status of any given shipment.
    For internal purposes only.
    """
    __tablename__ = "shipment_status"
    shipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("shipments.shipment_id"), primary_key=True
    )
    status_message: Mapped[Status]


class Warehouse(Base):
    """
    A warehouse that is used to store items and fulfill orders.
    """
    __tablename__ = "warehouses"
    warehouse_id: Mapped[UUID] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(VARCHAR(255))
    latitude: Mapped[float]
    longitude: Mapped[float]
    items: Mapped[list["WarehouseItem"]] = relationship()


class MockShipmentIDs(Base):
    """
    Database to hold mock tracking numbers and hard coded statuses
    """
    __tablename__ = "mock_shipment_ids"
    shipment_id: Mapped[UUID] = mapped_column(primary_key=True)
    tracking_number: Mapped[int]
    status: Mapped[Status] = mapped_column(VARCHAR(100))
