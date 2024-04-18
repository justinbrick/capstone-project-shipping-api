"""
A router to get user related shipping information.
"""

from fastapi import APIRouter
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import get_db
from app.auth.dependencies import get_profile
from app.auth.profile import AccountProfile
from app.shipping.models import Shipment, ShipmentStatus
from app.shipping.delivery import shipping_providers as shipping_providers
from app.database import schemas

router = APIRouter()
"""
Fix router to use correct queries in order to find shipments.
"""


@router.get("/shipments")
async def get_user_shipments(profile: AccountProfile = Depends(get_profile), db: Session = Depends(get_db)) -> list[Shipment]:
    """
    Get all the shipments for a given user.
    """

    return db.query(schemas.Shipment)\
        .join(schemas.ShipmentDeliveryInfo, schemas.Shipment.shipment_id == schemas.ShipmentDeliveryInfo.shipment_id)\
        .join(schemas.Delivery, schemas.ShipmentDeliveryInfo.delivery_id == schemas.Delivery.delivery_id)\
        .join(schemas.Order, schemas.Delivery.order_id == schemas.Order.order_id)\
        .where(schemas.Order.customer_id == profile.user_id)\
        .all()


@router.get("/shipments/{shipment_id}/status")
async def get_my_shipment_status(shipment_id: UUID, profile: AccountProfile = Depends(get_profile), db: Session = Depends(get_db)) -> ShipmentStatus:
    """
    Get the status of a shipment for the currently logged in user.
    """

    shipment = db.query(schemas.Shipment)\
        .join(schemas.ShipmentDeliveryInfo, schemas.Shipment.shipment_id == schemas.ShipmentDeliveryInfo.shipment_id)\
        .join(schemas.Delivery, schemas.ShipmentDeliveryInfo.delivery_id == schemas.Delivery.delivery_id)\
        .join(schemas.Order, schemas.Delivery.order_id == schemas.Order.order_id)\
        .where(schemas.Order.customer_id == profile.user_id)\
        .where(schemas.Shipment.shipment_id == shipment_id)\
        .first()

    return await shipping_providers[shipment.provider].get_shipment_status(shipment.provider_shipment_id)


def sort_all_shipments(shipments):
    """
    Sort the shipments by created_at field in descending order
    """

    return sorted(shipments, key=lambda shipment: shipment["created_at"], reverse=True)


def sort_out_undelivered_shipments(shipments):
    """
    Sort out the shipments that are not delivered yet
    """

    return [shipment for shipment in shipments if shipment["status"] != ShipmentStatus.DELIVERED]


def sort_out_delivered_shipments(shipments):
    """
    Sort out the shipments that are delivered
    """

    return [shipment for shipment in shipments if shipment["status"] == ShipmentStatus.DELIVERED]
