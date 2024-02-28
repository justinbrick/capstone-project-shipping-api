from uuid import UUID

class Order:
    order_id: UUID
    customer_id: UUID
    
    def __init__(self, order_id: UUID, customer_id: UUID) -> None:
        self.order_id = order_id
        self.customer_id = customer_id

    def get_items():
        pass
        
