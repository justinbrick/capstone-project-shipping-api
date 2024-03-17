from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from . import schemas
from ..models.shipment import Shipment, ShipmentStatus



def create_shipment(db: Session, shipment: Shipment) -> schemas.Shipment:
    """
    Save the shipment to the database.
    """
    new_shipment_id = uuid4()
    provider_shipment_id = "1234"
    created_shipment = schemas.Shipment(**shipment.model_dump(), shipment_id=new_shipment_id, provider_shipment_id=provider_shipment_id)
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
    shipment = db.query(schemas.Shipment).filter(schemas.Shipment.shipment_id == shipment_id).first()
    return shipment

def get_shipment_items(shipment_id: UUID) -> list[tuple[int, int]]:
    """
    Given a shipment ID returns all of the shipment items that are registered under that specific shipment.

    :param shipment_id: the ID of the shipment to get 
    :return: A list of tuple[upc, stock], which represent the items & stock that the order contains.
    """
    pass

def get_shipment_status(shipment_id: UUID) -> ShipmentStatus:
    """
    Get the status for a shipment, given a shipment ID.
    """
    pass