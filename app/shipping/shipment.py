"""
Business functions for creating low level shipments.
"""

__author__ = "Justin B. (justin@justin.directory)"


from app.shipping.delivery import shipping_providers
from app.shipping.models import CreateShipmentRequest, Shipment


async def create_shipment(request: CreateShipmentRequest) -> Shipment:
    """
    Create a shipment with the given request.
    """
    provider = shipping_providers[request.provider]
    shipment = await provider.create_shipment(request)
    return shipment
