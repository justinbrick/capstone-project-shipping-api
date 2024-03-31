"""
In order to store models, they must be created using the declarative base in SQLAlchemy.
This base class is used to create the tables and metadata for the database.
All models must inherit from this base class, or it won't be created.
"""

from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey
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
    shipping_address: Mapped[str]
    provider: Mapped[Provider]
    provider_shipment_id: Mapped[str]
    created_at: Mapped[datetime]
    items: Mapped[list["ShipmentItem"]] = relationship()


class ShipmentDeliveryInfo(Base):
    """
    A table to store the delivery information for a shipment.
    """
    __tablename__ = "shipment_delivery_info"
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipments.shipment_id"), primary_key=True)
    delivery_id: Mapped[UUID] = mapped_column(ForeignKey("deliveries.delivery_id"), primary_key=True)


class Delivery(Base):
    """
    Represents a full delivery, composed of the individual orders.
    """
    __tablename__ = "deliveries"
    delivery_id: Mapped[UUID] = mapped_column(primary_key=True)
    order_id: Mapped[UUID]
    created_at: Mapped[datetime]
    fulfilled_at: Mapped[datetime] = mapped_column(nullable=True)
    delivery_sla: Mapped[str]
    delivery_shipments: Mapped[list["ShipmentDeliveryInfo"]] = relationship()


class WarehouseItem(Base):
    """
    An item that is stored in a warehouse.
    """
    __tablename__ = "warehouse_items"
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouses.warehouse_id"), primary_key=True)
    upc: Mapped[int] = mapped_column(primary_key=True)
    stock: Mapped[int]


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
        ForeignKey("shipments.shipment_id"), primary_key=True)
    status_message: Mapped[Status]


class Warehouse(Base):
    """
    A warehouse that is used to store items and fulfill orders.
    """
    __tablename__ = "warehouses"
    warehouse_id: Mapped[UUID] = mapped_column(primary_key=True)
    address: Mapped[str]
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
    status: Mapped[str]
