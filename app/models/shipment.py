from pydantic import BaseModel
from uuid import UUID

class Shipment(BaseModel):
    """
    The shipment model represents a shipment that has been created for a specific order.
    Multiple shipments can be created for one order.
    """
    order_id: UUID
    shipment_id: UUID
    shipping_address: str
    provider: str
    provider_shipment_id: str

    model_config = {
        "from_attributes": True
    }
        
class CreateShipmentRequest(BaseModel):
    """
    The shipment request model represents a request to create a shipment regarding a specific order.
    This is not stored in any database and is rather just used so that we can create the shipment itself.
    """
    order_id: UUID
    shipping_address: str
    provider: str  # This might need to be an enum so the documentation generates the correct options.

class ShipmentStatus(BaseModel):
    """
    The status of a shipment - due to varying sources of shipment delivery, this must be put into one 
    unified response. 
    """
    order_id: UUID
    status: str



    