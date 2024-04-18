"""
A router for creating and managing deliveries.
"""

__author__ = "Justin B. (justin@justin.directory)"

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import get_db
from app.shipping.delivery import get_delivery_breakdown
from app.shipping.models import CreateDeliveryRequest, Delivery, Shipment, ShipmentDeliveryBreakdown
from app.database import schemas


router = APIRouter()


@router.get("/{delivery_id}/shipments", operation_id="get_delivery_shipments")
async def get_delivery_shipments(delivery_id: UUID, db: Session = Depends(get_db)) -> list[Shipment]:
    """
    Get all the shipments for a given delivery.
    """
    shipments = db.query(schemas.Shipment)\
        .join(schemas.ShipmentDeliveryInfo)\
        .where(schemas.ShipmentDeliveryInfo.delivery_id == delivery_id)\
        .all()

    return shipments


@router.post("/breakdown", operation_id="make_delivery_breakdown")
async def make_delivery_breakdown(request: CreateDeliveryRequest) -> ShipmentDeliveryBreakdown:
    """
    Make a delivery breakdown with the given request.
    """
    breakdown = await get_delivery_breakdown(request.recipient_address, request.delivery_sla, request.items)
    return breakdown
