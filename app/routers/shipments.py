"""
A router containing endpoints for getting shipment information & creating shipments.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.middleware.authenticate import require_roles, require_scopes
from app import get_db
from app.shipping.models import Shipment, ShipmentStatus
from app.shipping.delivery import shipping_providers as shipping_providers
from app.database import schemas

router = APIRouter()


@router.get("/{shipment_id}")
@require_scopes(["Shipment.Read"])
@require_roles(["Admin"])
async def get_shipment(shipment_id: UUID, db: Session = Depends(get_db)) -> Shipment:
    """
    Get the shipment using a specific shipment ID.
    This is the actual shipment - not the status of the shipment.
    """
    shipment = db.get(schemas.Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")
    return shipment


@router.get("/{shipment_id}/status")
@require_scopes(["Shipment.Read"])
async def get_shipment_status(shipment_id: UUID, db: Session = Depends(get_db)) -> ShipmentStatus:
    """
    Get the shipment status for a specific shipment ID.
    Due to varying providers, this is a delegate request.
    As a result, it is volatile depending on the provider.
    """
    shipment = await get_shipment(shipment_id, db)
    provider = shipping_providers[shipment.provider]
    status = await provider.get_shipment_status(shipment.provider_shipment_id)
    return status
