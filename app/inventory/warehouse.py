"""
Warehouse related requests.
"""

from uuid import UUID

from app.database import Session
from app.database.schemas import Warehouse
from app.shipping.location import get_address_coordinates

from geopy.distance import geodesic

from . import client


async def get_warehouses():
    """
    Get all warehouses.
    TODO: Get warehouse information from the warehouse API.
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


async def get_warehouse_stock(warehouse_id: UUID, upcs: list[int]) -> list[tuple[int, int]]:
    """
    Get the stock for a list of UPCs in a warehouse.
    """
    response = await client.post(f"/warehouses/{warehouse_id}/stock", json={"items": upcs})
    response.raise_for_status()
    return response.json()


async def get_nearest_warehouses(location: str) -> list[Warehouse]:
    """
    Get the 4 nearest warehouses to a given location.
    TODO: Move over to the warehouse API once it is implemented.
    """
    with Session() as db:
        coordinates = await get_address_coordinates(location)
        warehouses = db.query(Warehouse).all()
        nearest_warehouses = sorted(
            warehouses,
            key=lambda warehouse: geodesic(coordinates, (warehouse.latitude, warehouse.longitude)).miles
        )
        nearest_warehouses = nearest_warehouses[:4]

    return nearest_warehouses
