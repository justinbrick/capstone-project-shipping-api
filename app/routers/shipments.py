"""
A router containing endpoints for getting shipment information & creating shipments.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.middleware.authenticate import require_roles, require_scopes
from .. import get_db
from ..database import shipments as db_shipments
from ..shipping.models import CreateShipmentRequest, Provider, Shipment

router = APIRouter()


@router.post("/")
@require_scopes(["Shipment.Create"])
async def create_shipment(request: CreateShipmentRequest, db: Session = Depends(get_db)) -> Shipment:
    """
    Creates a shipment, given the request.
    """
    try:
        shipment = db_shipments.create_shipment(db, request)
        return shipment
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Could not create shipment.") from exc


@router.get("/{shipment_id}")
@require_scopes(["Shipment.Read"])
@require_roles(["Admin"])
async def get_shipment(shipment_id: UUID, db: Session = Depends(get_db)) -> Shipment:
    """
    Get the shipment using a specific shipment ID.
    This is the internal shipment - not the status of the shipment.
    """
    shipment = db_shipments.get_shipment(db, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")
    return shipment


@router.get("/{shipment_id}/status")
@require_scopes(["Shipment.Read"])
async def get_shipment_status(shipment_id: UUID, db: Session = Depends(get_db)):
    """
    Get the shipment status for a specific shipment ID.
    Due to varying providers, this is a delegate request.
    As a result, it is volatile depending on the provider.
    """
    shipment = await get_shipment(shipment_id, db)
    match shipment.provider:
        case Provider.INTERNAL:
            pass
        case Provider.UPS:
            pass
        case Provider.FEDEX:
            pass
        case Provider.USPS:
            pass
        case _:
            raise HTTPException(status_code=400, detail="Invalid provider.\nValid Providers: " +
                                ", ".join([provider.value for provider in Provider]))
    raise HTTPException(
        status_code=500, detail="Could not get shipment status. Has this provider been implemented?")


"Could the about function get rid of the match statement and just call the get_shipment_request function?"
