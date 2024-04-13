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


@router.get("/shipments")
async def get_user_shipments(profile: AccountProfile = Depends(get_profile), db: Session = Depends(get_db)) -> list[Shipment]:
    """
    Get all the shipments for a given user.
    """

    shipments = db.query(schemas.Shipment).where(
        schemas.Shipment.user_id == profile.user_id).all()

    return shipments


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
