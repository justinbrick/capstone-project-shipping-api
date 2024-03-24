"""
Database functions for warehouse
This is volatile and will be removed in the future, once inventory team has implemented the warehouse API.
"""

from ..shipping.location import get_address_coordinates
from .schemas import Warehouse
from sqlalchemy.orm import Session
from geopy.distance import geodesic


def get_nearest_warehouse(db: Session, location: str) -> Warehouse:
    """
    Get the nearest warehouse to a given location.
    """
    coordinates = get_address_coordinates(location)
    warehouses = db.query(Warehouse).all()

    nearest_warehouse = None
    nearest_distance = float("inf")

    for warehouse in warehouses:
        warehouse_coordinates = get_address_coordinates(warehouse.address)
        distance = geodesic(coordinates, warehouse_coordinates).miles
        if distance < nearest_distance:
            nearest_warehouse = warehouse
            nearest_distance = distance

    return nearest_warehouse
