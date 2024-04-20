"""
Queries for internal shipping.
This allows employees to mark shipments as delivered.
"""

__author__ = "Justin B. (justin@justin.directory)"

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_profile
from app.auth.profile import AccountProfile
from app.database import schemas
from app.database.dependencies import get_db
from app.parameters.pagination import PaginationParams
from app.parameters.shipment import FullShipmentQueryParams
from app.routers.shipments import get_shipments
from app.shipping.enums import Provider, Status
from app.shipping.models import Shipment

router = APIRouter()


@router.get("/open_shipments", operation_id="get_open_shipments")
async def get_open_shipments(params: PaginationParams = Depends(), db: Session = Depends(get_db)) -> list[Shipment]:
    """
    An endpoint which returns shipments that are internal, and in a pending status.
    This allows employees to take on individual shipments as needed.
    In a normal setting, this would require likely be automatically assigned to a driver.
    """
    params = FullShipmentQueryParams(
        limit=params.limit,
        offset=params.offset,
        date_desc=False,
        status=Status.PENDING,
        provider=Provider.INTERNAL
    )

    open_shipments = await get_shipments(params, db)
    return open_shipments


@router.post("/open_shipments/{shipment_id}/claim", operation_id="claim_open_shipment")
async def claim_shipment(shipment_id: UUID, profile: AccountProfile = Depends(get_profile), db: Session = Depends(get_db)) -> Shipment:
    """
    Claim a shipment for delivery.
    """
    shipment = db.get(schemas.Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")

    if shipment.provider != Provider.INTERNAL:
        raise HTTPException(
            status_code=400,
            detail="Shipment is not internal."
        )

    status = shipment.status

    if status.message != Status.PENDING:
        raise HTTPException(status_code=400, detail="Shipment is not pending.")

    status.updated_at = datetime.now()
    status.message = Status.SHIPPED

    reservation = schemas.ShippingEmployeeReservation(
        employee_id=profile.user_id,
        shipment_id=shipment_id
    )

    db.add(reservation)
    db.commit()

    return shipment
