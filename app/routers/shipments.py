from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from .. import get_db
from ..models.shipment import CreateShipmentRequest, Shipment
from ..database.shipments import create_shipment as db_create_shipment, get_shipment as db_get_shipment

router = APIRouter()

@router.post("/", response_model=Shipment)
async def create_shipment(request: CreateShipmentRequest, db: Session = Depends(get_db)) -> Shipment:
    try:
        shipment = db_create_shipment(db, request)
        
        return shipment
    except Exception:
        raise HTTPException(status_code=500, detail="Could not create shipment.")

@router.get("/{shipment_id}")
async def get_shipment_request(shipment_id: UUID, db: Session = Depends(get_db)) -> Shipment:
    """
    Get the shipment using a specific shipment ID.
    This is the internal shipment - not the status of the shipment.
    """
    shipment = db_get_shipment(db, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")
    return shipment

@router.get("/{shipment_id}/status")
async def get_shipment_status(shipment_id: UUID):
    """
    Get the shipment status for a specific shipment ID.
    Due to varying providers, this is a delegate request. As a result, it is volatile depending on the provider.
    """
    shipment = await get_shipment_request(shipment_id)
    match shipment.provider:
        case "internal":
            pass
        case "ups":
            pass
        case "fedex":
            pass
        case "usps":
            pass
        case _:
            pass
    return "Shipment status."