"""
All the models related to inventory management.
"""

__author__ = "Justin B. (justin@justin.directory)"


from uuid import UUID
from pydantic import BaseModel

from app.database.schemas import WarehouseItem
from app.shipping.models import ShipmentItem


class WarehouseStockAvailability(BaseModel):
    """
    Represents the availability of items in a warehouse.
    """
    warehouse_id: UUID
    """The ID of the warehouse."""
    items: list[ShipmentItem]
