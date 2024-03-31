"""
Business logic regarding the delivery of shipments.
"""

from datetime import datetime, timedelta
from random import choice
from app.database.schemas import Warehouse
from app.inventory.warehouse import get_nearest_warehouses, get_warehouse_stock
from app.shipping.models import DeliveryTimeResponse, ShipmentDeliveryBreakdown, ShipmentItem
from .enums import SLA, Provider
from .providers import ShipmentProvider, fedex, internal, ups, usps


available_providers: dict[Provider, ShipmentProvider] = {
    Provider.FEDEX: fedex.client,
    Provider.UPS: ups.client,
    Provider.USPS: usps.client,
    Provider.INTERNAL: internal.client
}


async def get_delivery_breakdown(address: str, sla: SLA, items: list[ShipmentItem]) -> list[DeliveryTimeResponse]:
    """
    Get a delivery breakdown given a specific SLA and items.
    """
    # Logic to determine the delivery breakdown.
    delivery_times: list[DeliveryTimeResponse] = []
    nearest_warehouses = await get_nearest_warehouses(address)
    warehouse_chunks: dict[Warehouse, list[ShipmentItem]] = {}
    """For each warehouse, get the available warehouse."""
    for warehouse in nearest_warehouses:
        # TODO: improve get_warehouse_stock
        warehouse_stock = await get_warehouse_stock(warehouse.warehouse_id, [item.upc for item in items])
        warehouse_chunks[warehouse] = warehouse_stock
    return delivery_times