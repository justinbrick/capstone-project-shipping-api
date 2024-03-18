"""
In order to store models, they must be created using the declarative base in SQLAlchemy.
This base class is used to create the tables and metadata for the database.
All models must inherit from this base class, or it won't be created.
"""

from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ..models.shipment import Provider, Status


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
    order_id: Mapped[UUID]
    shipping_address: Mapped[str]
    provider: Mapped[Provider]
    provider_shipment_id: Mapped[str]
    created_at: Mapped[datetime]
    items: Mapped[list["ShipmentItem"]] = relationship()


class ShipmentItem(Base):
    """
    A shipment item that is related to a given shipment.
    There can be multiple items associated with one shipment.
    """
    __tablename__ = "shipment_items"
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipments.shipment_id"), primary_key=True)
    upc: Mapped[int] = mapped_column(primary_key=True)
    stock: Mapped[int]


class ShipmentStatus(Base):
    """
    The status of any given shipment. 
    For internal purposes only.
    """
    __tablename__ = "shipment_status"
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipments.shipment_id"), primary_key=True)
    status_message: Mapped[Status]
