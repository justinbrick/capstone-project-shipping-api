from pydantic import BaseModel
from uuid import UUID, uuid4
from ..database import connection

class Shipment(BaseModel):
    """
    The shipment model represents a shipment that has been created for a specific order.
    """
    order_id: UUID
    shipment_id: UUID
    shipping_address: str
    provider: str
    provider_shipment_id: str
        
class ShipmentRequest(BaseModel):
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

def create_shipment(request: ShipmentRequest):
    """
    From a shipment, create a request which we will use to correlate a shipment to an order.
    """
    shipment_id = uuid4()
    shipment = Shipment(order_id=request.order_id, shipment_id=shipment_id, shipping_address=request.shipping_address, provider=request.provider, provider_shipment_id="1234")
    return shipment
    

    