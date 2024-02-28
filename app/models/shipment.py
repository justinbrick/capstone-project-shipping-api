from pydantic import BaseModel
from uuid import UUID


class Shipment:

    def __init__(self) -> None:
        pass

"""
The shipment request model represents a request to create a shipment regarding a specific order.

"""
class ShipmentRequest(BaseModel):
    
    def __init__(self, shipment_id: UUID, shipping_address: str, provider: str) -> None:
        self.shipment_id: UUID = shipment_id
        self.shipping_address: str = shipping_address
        self.provider: str = provider