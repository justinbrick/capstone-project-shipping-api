from fastapi import APIRouter, HTTPException
from uuid import UUID

from ..models.shipment import ShipmentRequest, Shipment, create_shipment
from ..database import shipments as shipment_db
from ..database import ColumnNotFoundException, ColumnInsertionException

router = APIRouter()

@router.post("/")
async def create_shipment_request(request: ShipmentRequest) -> Shipment:
    try:
        shipment = create_shipment(request)
        shipment_db.save_shipment(shipment)
        return shipment
    except ColumnInsertionException:
        raise HTTPException(status_code=500, detail=f"There was an error creating your shipment.")

@router.get("/{shipment_id}")
async def get_shipment_request(shipment_id: UUID) -> Shipment:
    """
    Get the shipment using a specific shipment ID.
    This is the internal shipment - not the status of the shipment.
    """
    try:
        shipment = shipment_db.get_shipment(shipment_id)
        return shipment
    except ColumnNotFoundException:
        raise HTTPException(status_code=404, detail=f"Could not find a shipment @ \"{shipment_id}\"")

@router.get("/{shipment_id}/status")
async def get_shipment_status(shipment_id: UUID):
    """
    Get the shipment status for a specific shipment ID.
    Due to varying providers, this is a delegate request. As a result, it is volatile depending on the provider.
    """
    shipment = await get_shipment_request(shipment_id)
    match shipment.provider:
        case "internal":
            status = shipment_db.get_shipment_status(shipment_id)
        case "ups":
            pass
        case "fedex":
            pass
        case "usps":
            pass
        case _:
            pass
    return "Shipment status."