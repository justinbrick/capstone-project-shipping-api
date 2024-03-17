from pydantic import BaseModel
from uuid import UUID

class Order:
    order_id: UUID
    customer_id: UUID

    
        
