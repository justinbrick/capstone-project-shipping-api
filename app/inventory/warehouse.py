"""
Warehouse related requests.
"""

from uuid import UUID
from . import client


async def get_warehouses():
    """
    Get all warehouses.
    """
    response = await client.get("/warehouses")
    response.raise_for_status()
    return response.json()


async def get_warehouse(warehouse_id: UUID):
    """
    Get a warehouse by its ID.
    """
    response = await client.get(f"/warehouses/{warehouse_id}")
    response.raise_for_status()
    return response.json()


async def get_warehouse_stock(warehouse_id: UUID, upcs: list[int]):
    """
    Get the stock for a list of UPCs in a warehouse.
    """
    response = await client.post(f"/warehouses/{warehouse_id}/stock", json={"items": upcs})
    response.raise_for_status()
    return response.json()

