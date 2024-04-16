"""
A router containing endpoints for getting shipment information & creating shipments.
"""

__author__ = "Justin B. (justin@justin.directory)"

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import get_db
from app.auth.dependencies import get_profile
from app.auth.profile import AccountProfile
from app.shipping.models import Shipment, ShipmentStatus
from app.shipping.delivery import shipping_providers as shipping_providers
from app.database import schemas

router = APIRouter()


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: UUID, db: Session = Depends(get_db)) -> Shipment:
    """
    Get the shipment using a specific shipment ID.

    :param shipment_id: the ID of the shipment to get
    :return: the shipment
    """
    shipment = db.get(schemas.Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")
    return shipment


@router.get("/")
async def get_shipments(db: Session = Depends(get_db), profile: AccountProfile = Depends(get_profile)) -> list[Shipment]:
    """
    Get all the shipments related to this user.

    :return: a list of shipments
    """
    profile_id = profile.user_id

    # Shipment -> ShipmentDeliveryInfo -> Delivery -> Order
    return db.query(schemas.Shipment)\
        .join(schemas.ShipmentDeliveryInfo, schemas.Shipment.shipment_id == schemas.ShipmentDeliveryInfo.shipment_id)\
        .join(schemas.Delivery, schemas.ShipmentDeliveryInfo.delivery_id == schemas.Delivery.delivery_id)\
        .join(schemas.Order, schemas.Delivery.order_id == schemas.Order.order_id)\
        .where(schemas.Order.customer_id == profile_id)\
        .all()


@router.get("/{shipment_id}/status")
async def get_shipment_status(shipment_id: UUID, db: Session = Depends(get_db)) -> ShipmentStatus:
    """
    Get the current status of a shipment.
    Queries third parties - expect failures.
    """

    shipment = await get_shipment(shipment_id, db)
    provider = shipping_providers[shipment.provider]
    status = await provider.get_shipment_status(shipment.provider_shipment_id)
    return status
