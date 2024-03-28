"""
In shipments, this contains functions used to get / modify shipments in our database.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..shipping.models import CreateShipmentRequest, ShipmentStatus
from . import schemas


def create_shipment(db: Session, shipment: CreateShipmentRequest) -> schemas.Shipment:
    """
    Save the shipment to the database.
    """
    new_shipment_id = uuid4()
    provider_shipment_id = "1234"
    created_at = datetime.now()
    created_shipment = schemas.Shipment(
        **shipment.model_dump(),
        shipment_id=new_shipment_id,
        provider_shipment_id=provider_shipment_id,
        created_at=created_at)

    db.add(created_shipment)
    db.commit()
    db.refresh(created_shipment)
    return created_shipment


def get_shipment(db: Session, shipment_id: UUID) -> schemas.Shipment:
    """
    Get the shipment from the database, using the shipment ID.

    :param shipment_id: the ID of the shipment to get
    :return: the shipment object
    """
    shipment = db.query(schemas.Shipment).filter(
        schemas.Shipment.shipment_id == shipment_id).first()
    return shipment


def get_shipment_items(db: Session, shipment_id: UUID) -> list[tuple[int, int]]:
    """
    Given a shipment ID returns all of the shipment items that are registered under that specific shipment.

    :param shipment_id: the ID of the shipment to get
    :return: A list of tuple[upc, stock], which represent the items & stock that the order contains.
    """


def get_shipment_status(db: Session, shipment_id: UUID) -> ShipmentStatus:
    """
    Get the status for a shipment, given a shipment ID.
    Only works for internal shipments.

    :param db: the database session
    :param shipment_id: the ID of the shipment to get
    :return: the shipment status
    """
    shipment_status = db.query(schemas.ShipmentStatus).filter(
        schemas.ShipmentStatus.shipment_id == shipment_id).first()
    return shipment_status


def get_mock_shipping_status(db: Session, tracking_number: int) -> str:
    """
    Get the status of a package with a given tracking number.

    :param tracking_number: the tracking number to get the status for
    :return: the status of the package
    """
    shipment_status = db.query(schemas.ShipmentStatus).filter(
        schemas.ShipmentStatus.tracking_number == tracking_number).first()
    return shipment_status
