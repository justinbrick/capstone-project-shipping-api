from fastapi import APIRouter
from uuid import UUID

from ..models.shipment import ShipmentRequest, Shipment, create_shipment
from ..database.shipments import save_shipment

router = APIRouter()

@router.post("/")
async def create_shipment_request(request: ShipmentRequest) -> Shipment:
    shipment = create_shipment(request)
    save_shipment(shipment)
    return shipment

@router.get("/{shipment_id}")
async def get_shipment(shipment_id: UUID):
    return "Shipment."

@router.get("/{shipment_id}/status")
async def get_shipment_status(shipment_id: UUID):
    return "Shipment status."