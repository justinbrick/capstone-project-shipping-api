from fastapi import APIRouter
from uuid import UUID

from ..models.shipment import Shipment

router = APIRouter()

@router.post("/")
async def create_shipment(request: Shipment):
    return "Created shipment."

@router.get("/{shipment_id}")
async def get_shipment(shipment_id: UUID):
    return "Shipment."

@router.get("/{shipment_id}/status")
async def get_shipment_status(shipment_id: UUID):
    return "Shipment status."