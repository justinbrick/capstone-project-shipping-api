"""
A router for creating and managing deliveries.
"""

from fastapi import APIRouter

from app.shipping.models import CreateDeliveryRequest, Delivery


router = APIRouter()

@router.post("/")
async def create_delivery(request: CreateDeliveryRequest) -> Delivery:
    """
    Create a delivery.
    """
    
    