"""
Warehouse related requests.
"""

__author__ = "Justin B. (justin@justin.directory)"

from uuid import UUID

from geopy.distance import geodesic

from app.database import Session, schemas
from app.database.schemas import Warehouse
from app.inventory.models import WarehouseStockAvailability
from app.shipping.location import get_address_coordinates
from app.shipping.models import ShipmentItem

from . import client


class OutOfStockException(Exception):
    """Raised when there is not enough stock to fulfill an order."""


async def get_warehouses() -> list[Warehouse]:
    """
    Get all warehouses.
    TODO: Get warehouse information from the warehouse API.
    """
    response = await client.get("/warehouses")
    response.raise_for_status()
    return response.json()


async def get_warehouse(warehouse_id: UUID) -> Warehouse:
    """
    Get a warehouse by its ID.
    """
    """TEST IMPL, VOLATILE!"""
    with Session() as db:
        warehouse = db.get(Warehouse, warehouse_id)
        return warehouse

    response = await client.get(f"/warehouses/{warehouse_id}")
    response.raise_for_status()
    return response.json()


async def get_warehouse_by_address(address: str) -> Warehouse:
    """
    Get a warehouse by its address.

    :param address: the address of the warehouse
    """
    """TEST IMPL, VOLATILE!"""
    with Session() as db:
        warehouse = db.query(Warehouse).filter(
            Warehouse.address == address).first()
        if warehouse is None:
            raise ValueError("Warehouse not found.")
        return warehouse

    response = await client.get(f"/warehouses/address/{address}")
    response.raise_for_status()
    return response.json()


async def get_warehouse_stock(warehouse_id: UUID, upcs: list[int]) -> list[ShipmentItem]:
    """
    Get the stock for a list of UPCs in a warehouse.
    """
    """TEST IMPL, VOLATILE!"""
    with Session() as db:
        items = db.query(schemas.WarehouseItem)\
            .filter(schemas.WarehouseItem.warehouse_id == warehouse_id)\
            .filter(schemas.WarehouseItem.upc.in_(upcs))\
            .all()

        return items

    response = await client.post(f"/warehouses/{warehouse_id}/stock", json={"items": upcs})
    response.raise_for_status()
    return response.json()


async def get_warehouse_stock_availability(warehouse_id: UUID, items: list[ShipmentItem]) -> WarehouseStockAvailability:
    """
    For a given warehouse, and a list of items with their UPC & stock, get the items available by UPC.
    Returns min(warehouse.stock, item.stock) for each item.
    Mutates the stock of the items in the list.

    :param warehouse_id: the ID of the warehouse
    :param items: the items to check the stock for
    """
    warehouse_stock = await get_warehouse_stock(warehouse_id, [item.upc for item in items])
    warehouse_stock_map = {item.upc: item.stock for item in warehouse_stock}
    stock_availability = []
    for item in items:
        min_value = min(warehouse_stock_map[item.upc], item.stock)
        stock_availability.append(ShipmentItem(
            upc=item.upc,
            stock=min_value
        ))
        item.stock -= min_value
    return WarehouseStockAvailability(warehouse_id=warehouse_id, items=stock_availability)


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
            key=lambda warehouse: geodesic(
                coordinates, (warehouse.latitude, warehouse.longitude)).miles
        )
        nearest_warehouses = nearest_warehouses[:4]

    return nearest_warehouses


async def get_warehouse_chunks(address: str, items: list[ShipmentItem]) -> list[WarehouseStockAvailability]:
    """
    Get a delivery breakdown given a specific SLA and items.
    If the order cannot be fulfilled, raise an OutOfStockException.

    :param address: the address to deliver to
    :param items: the items to deliver
    """
    items_left = [item.model_copy() for item in items if item.stock > 0]
    nearest_warehouses = await get_nearest_warehouses(address)
    warehouse_chunks = []

    for warehouse in nearest_warehouses:

        if len(items_left) == 0:
            break

        warehouse_stock = await get_warehouse_stock_availability(warehouse.warehouse_id, items_left)
        warehouse_chunks.append(warehouse_stock)
        items_left = [item for item in items_left if item.stock > 0]

    if len(items_left) > 0:
        raise OutOfStockException("Not enough stock to fulfill the order.")

    return warehouse_chunks


async def remove_warehouse_stock(warehouse_id: UUID, items: list[ShipmentItem]):
    """
    Remove stock from a warehouse.
    """
    """TEST IMPL, VOLATILE!"""
    with Session() as db:
        for item in items:
            db_item = db.query(schemas.WarehouseItem)\
                .filter(schemas.WarehouseItem.warehouse_id == warehouse_id)\
                .filter(schemas.WarehouseItem.upc == item.upc)\
                .first()

            db_item.stock -= item.stock

        db.flush()
        db.commit()

    # response = await client.post(f"/warehouses/{warehouse_id}/stock/remove", json={"items": items})
    # response.raise_for_status()
    # return response.json()


async def add_warehouse_stock(warehouse_id: UUID, items: list[ShipmentItem]):
    """
    Add stock to a warehouse.
    """
    """TEST IMPL, VOLATILE!"""
    with Session() as db:
        for item in items:
            db_item = db.query(schemas.WarehouseItem)\
                .filter(schemas.WarehouseItem.warehouse_id == warehouse_id)\
                .filter(schemas.WarehouseItem.upc == item.upc)\
                .first()

            db_item.stock += item.stock

        db.flush()
        db.commit()

    # response = await client.post(f"/warehouses/{warehouse_id}/stock/add", json={"items": items})
    # response.raise_for_status()
    # return response.json()
