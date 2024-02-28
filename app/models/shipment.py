from pydantic import BaseModel
from uuid import UUID

class Shipment(BaseModel):
    """
    The shipment model represents a shipment that has been created for a specific order.
    """

    order_id: UUID
    shipment_id: UUID
    shipping_address: str
    provider: str
    provider_shipment_id: str

    def __init__(self, order_id: UUID, shipment_id: UUID, shipping_address: str, provider: str, provider_shipment_id: str) -> None:
        self.order_id = order_id
        self.shipment_id = shipment_id
        self.shipping_address = shipping_address
        self.provider = provider
        self.provider_shipment_id = provider_shipment_id
        
class ShipmentRequest(BaseModel):
    """
    The shipment request model represents a request to create a shipment regarding a specific order.
    This is not stored in any database and is rather just used so that we can create the shipment itself.
    """
    
    order_id: UUID
    shipping_address: str
    provider: str  # This might need to be an enum so the documentation generates the correct options.

    def __init__(self, order_id: UUID, shipping_address: str, provider: str) -> None:
        self.order_id: UUID = order_id
        self.shipping_address: str = shipping_address
        self.provider: str = provider

def create_shipment(request: ShipmentRequest):
    pass