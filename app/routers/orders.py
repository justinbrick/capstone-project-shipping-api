"""
All the routes to get shipping information related to billing orders.
"""

from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db, schemas
from ..shipping.models import CreateDeliveryRequest, Delivery

router = APIRouter()


@router.get("{order_id}/deliveries")
async def get_order_deliveries(order_id: UUID, db: Session = Depends(get_db)) -> list[Delivery]:
    """
    Get all the deliveries for a given order.
    """
    deliveries = db.query(schemas.Delivery)\
        .where(schemas.Delivery.order_id == order_id)\
        .all()

    if len(deliveries) == 0:
        raise HTTPException(status_code=404, detail="No deliveries found for the given order.")

    return deliveries


@router.post("{order_id}/deliveries", status_code=201)
async def create_order_delivery(order_id: UUID, delivery: CreateDeliveryRequest, db: Session = Depends(get_db)) -> Delivery:
    """
    Create a delivery for a given order.
    """
    delivery_id = uuid4()
    # TODO: Logic to get items from cart and break them down into shipments.
    
    db_delivery = schemas.Delivery(
        delivery_id=delivery_id,
        order_id=order_id,
        created_at=delivery.created_at,
        delivery_sla=delivery.delivery_sla
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)

    return db_delivery
