from uuid import UUID

class Order:
    def __init__(self, order_id: UUID) -> None:
        self.order_id: UUID = order_id
        self.order_items: list = []
        
