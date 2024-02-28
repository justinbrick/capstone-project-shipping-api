from fastapi import APIRouter

from ..models.shipment import ShipmentRequest

router = APIRouter()

@router.post("/")
async def create_shipment(request: ShipmentRequest):
    return "Created shipment."