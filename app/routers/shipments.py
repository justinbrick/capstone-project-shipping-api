from fastapi import APIRouter
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
    shipment = shipment_db.get_shipment(shipment_id)
    return shipment

@router.get("/{shipment_id}/status")
async def get_shipment_status(shipment_id: UUID):
    return "Shipment status."

