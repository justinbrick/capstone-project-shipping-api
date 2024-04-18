"""
Get information relevant to the currently logged in user.
"""

__author__ = "Justin B. (justin@justin.directory)"

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import get_db
from app.auth.dependencies import get_profile
from app.auth.profile import AccountProfile
from app.database import schemas
from app.shipping.models import Delivery, Shipment, ShipmentStatus
from app.shipping.delivery import shipping_providers

router = APIRouter()


@router.get("/shipments", operation_id="get_personal_shipments")
async def get_my_shipments(db: Session = Depends(get_db), profile: AccountProfile = Depends(get_profile)) -> list[Shipment]:
    """
    Get all the shipments related to the currently logged in user.
    """
    profile_id = profile.user_id

    # Shipment -> ShipmentDeliveryInfo -> Delivery -> Order
    return db.query(schemas.Shipment)\
        .join(schemas.ShipmentDeliveryInfo, schemas.Shipment.shipment_id == schemas.ShipmentDeliveryInfo.shipment_id)\
        .join(schemas.Delivery, schemas.ShipmentDeliveryInfo.delivery_id == schemas.Delivery.delivery_id)\
        .join(schemas.Order, schemas.Delivery.order_id == schemas.Order.order_id)\
        .where(schemas.Order.customer_id == profile_id)\
        .all()


@router.get("/shipments/{shipment_id}/status", operation_id="get_personal_shipment_status")
async def get_my_shipment_status(shipment_id: UUID, db: Session = Depends(get_db), profile: AccountProfile = Depends(get_profile)) -> ShipmentStatus:
    """
    Get the status of a shipment for the currently logged in user.
    """
    profile_id = profile.user_id

    related_shipment = db.query(schemas.Shipment)\
        .join(schemas.ShipmentDeliveryInfo, schemas.Shipment.shipment_id == schemas.ShipmentDeliveryInfo.shipment_id)\
        .join(schemas.Delivery, schemas.ShipmentDeliveryInfo.delivery_id == schemas.Delivery.delivery_id)\
        .join(schemas.Order, schemas.Delivery.order_id == schemas.Order.order_id)\
        .where(schemas.Order.customer_id == profile_id)\
        .where(schemas.Shipment.shipment_id == shipment_id)\
        .first()

    if related_shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")

    provider = shipping_providers[related_shipment.provider]
    status = await provider.get_shipment_status(related_shipment.provider_shipment_id)

    return status


@router.get("/deliveries", operation_id="get_personal_deliveries")
async def get_my_deliveries(db: Session = Depends(get_db), profile: AccountProfile = Depends(get_profile)) -> list[Delivery]:
    """
    Get all the deliveries related to this user.
    """
    profile_id = profile.user_id

    return db.query(schemas.Delivery)\
        .join(schemas.Order, schemas.Delivery.order_id == schemas.Order.order_id)\
        .where(schemas.Order.customer_id == profile_id)\
        .all()
