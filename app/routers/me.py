"""
Get information relevant to the currently logged in user.
"""

__author__ = "Justin B. (justin@justin.directory)"

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_profile
from app.auth.profile import AccountProfile
from app.database.dependencies import get_db
from app.parameters.shipment import BaseShipmentQueryParams
from app.routers.users import (get_user_deliveries, get_user_shipment_status,
                               get_user_shipments)
from app.shipping.models import Delivery, Shipment, ShipmentStatus

router = APIRouter()


@router.get("/shipments", operation_id="get_personal_shipments")
async def get_my_shipments(params: BaseShipmentQueryParams = Depends(), profile: AccountProfile = Depends(get_profile), db: Session = Depends(get_db)) -> list[Shipment]:
    """
    Get all the shipments related to the currently logged in user.
    """
    profile_id = profile.user_id

    return await get_user_shipments(profile_id, params, db)


@router.get("/shipments/{shipment_id}/status", operation_id="get_personal_shipment_status")
async def get_my_shipment_status(shipment_id: UUID, db: Session = Depends(get_db), profile: AccountProfile = Depends(get_profile)) -> ShipmentStatus:
    """
    Get the status of a shipment for the currently logged in user.
    """
    profile_id = profile.user_id

    return await get_user_shipment_status(shipment_id, profile_id, db)


@router.get("/deliveries", operation_id="get_personal_deliveries")
async def get_my_deliveries(db: Session = Depends(get_db), profile: AccountProfile = Depends(get_profile)) -> list[Delivery]:
    """
    Get all the deliveries related to this user.
    """
    profile_id = profile.user_id

    return await get_user_deliveries(profile_id, db)
