"""
Business functions for creating low level shipments.
"""

from app.shipping.delivery import available_providers
from app.shipping.models import CreateShipmentRequest, Shipment


async def create_shipment(request: CreateShipmentRequest) -> Shipment:
    """
    Create a shipment with the given request.
    """
    provider = available_providers[request.provider]
    shipment = await provider.create_shipment(request)
    return shipment
