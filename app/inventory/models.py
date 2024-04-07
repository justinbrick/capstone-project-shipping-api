"""
All the models related to inventory management.
"""

from pydantic import BaseModel

from app.database.schemas import WarehouseItem
from app.shipping.models import ShipmentItem


class WarehouseStockAvailability(BaseModel):
    """
    Represents the availability of items in a warehouse.
    """
    warehouse_id: int
    """The ID of the warehouse."""
    items: list[ShipmentItem]
