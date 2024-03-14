from fastapi import APIRouter, HTTPException
from uuid import UUID

from ..models.shipment import ShipmentRequest, Shipment, create_shipment
from ..database import shipments as shipment_db

router = APIRouter()

@router.post("/")
async def create_shipment_request(request: ShipmentRequest) -> Shipment:
    shipment = create_shipment(request)
    shipment_db.save_shipment(shipment)
    return shipment

@router.get("/{shipment_id}")
async def get_shipment_request(shipment_id: UUID) -> Shipment:
    try:
        shipment = shipment_db.get_shipment(shipment_id)
        return shipment
    except Exception:
        raise HTTPException(status_code=404)

@router.get("/{shipment_id}/status")
async def get_shipment_status(shipment_id: UUID):
    shipment = shipment_db.get_shipment(shipment_id)
    match shipment.provider:
        case "internal":
            status = shipment_db.get_shipment_status(shipment_id)
        case "ups":
            pass
        case "fedex":
            pass
        case _:
            pass
    return "Shipment status."

