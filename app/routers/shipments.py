"""
A router containing endpoints for getting shipment information & creating shipments.
"""

__author__ = "Justin B. (justin@justin.directory)"

from datetime import datetime
from uuid import UUID

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import cast
from sqlalchemy.orm import Session

from app.auth.dependencies import get_profile
from app.auth.profile import AccountProfile
from app.database import schemas
from app.database.dependencies import get_db
from app.parameters.shipment import FullShipmentQueryParams
from app.shipping.delivery import shipping_providers
from app.shipping.enums import Provider
from app.shipping.models import (Shipment, ShipmentStatus,
                                 ShipmentStatusPatchRequest)

router = APIRouter()


@router.get("/{shipment_id}", operation_id="get_shipment")
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


@router.get("/", operation_id="get_shipments")
async def get_shipments(params: FullShipmentQueryParams = Depends(), db: Session = Depends(get_db)) -> list[Shipment]:
    """
    Get all the shipments related to this user.
    """

    query = db.query(schemas.Shipment)

    # If we have a filter that requires table joins, we add them here.
    if params.delivery_id is not None or params.user_id is not None:
        query = query.join(schemas.Shipment.delivery)

    # Same for delivery ID, but requires additional joins.
    if params.user_id is not None:
        query = query\
            .join(schemas.Delivery.order)\
            .filter(schemas.Order.customer_id == params.user_id)

    if params.delivery_id is not None:
        query = query.filter(
            cast(
                schemas.Delivery.delivery_id, sqlalchemy.String
            ).ilike(
                f"%{params.delivery_id}%"
            )
        )

    if params.provider is not None:
        query = query.filter(schemas.Shipment.provider == params.provider)

    if params.status is not None:
        query = query\
            .join(schemas.Shipment.status)\
            .filter(schemas.ShipmentStatus.message == params.status)

    if params.from_address is not None:
        query = query.filter(schemas.Shipment.from_address.ilike(
            f"%{params.from_address}%"))

    if params.shipping_address is not None:
        query = query.filter(schemas.Shipment.shipping_address.ilike(
            f"%{params.shipping_address}%"))

    if params.tracking_id is not None:
        query = query.filter(schemas.Shipment.provider_shipment_id.ilike(
            f"%{params.tracking_id}%"))

    if params.date_desc:
        query = query.order_by(schemas.Shipment.created_at.desc())
    else:
        query = query.order_by(schemas.Shipment.created_at.asc())

    query = query.limit(params.limit).offset(params.offset)

    return query.all()


@router.get("/{shipment_id}/status", operation_id="get_shipment_status")
async def get_shipment_status(shipment_id: UUID, db: Session = Depends(get_db)) -> ShipmentStatus:
    """
    Get the current status of a shipment.
    Queries third parties - expect failures.
    """

    shipment = await get_shipment(shipment_id, db)
    provider = shipping_providers[shipment.provider]
    status = await provider.get_shipment_status(shipment.provider_shipment_id)
    return status


@router.patch("/{shipment_id}/status", operation_id="update_shipment_status")
async def update_shipment_status(shipment_id: UUID, status: ShipmentStatusPatchRequest, db: Session = Depends(get_db), profile: AccountProfile = Depends(get_profile)) -> ShipmentStatus:
    """
    Update the status of a shipment.
    """

    shipment = db.get(schemas.Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")

    if shipment.reservation is None or shipment.reservation.employee_id != profile.user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot update shipment status for unreserved shipments."
        )

    if shipment.provider is not Provider.INTERNAL:
        raise HTTPException(
            status_code=400,
            detail="Cannot update shipment status for non-internal shipments."
        )

    shipment.status.message = status.message
    shipment.status.updated_at = datetime.now()

    db.commit()

    return shipment.status
