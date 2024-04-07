"""
A router for creating and managing deliveries.
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import get_db
from app.shipping.models import CreateDeliveryRequest, Delivery, Shipment
from app.database import schemas


router = APIRouter()


@router.get("/{delivery_id}/shipments")
async def get_delivery_shipments(delivery_id: UUID, db: Session = Depends(get_db)) -> list[Shipment]:
    """
    Get all the shipments for a given delivery.
    """
    shipments = db.query(schemas.Shipment)\
        .join(schemas.ShipmentDeliveryInfo)\
        .where(schemas.ShipmentDeliveryInfo.delivery_id == delivery_id)\
        .all()

    return shipments
