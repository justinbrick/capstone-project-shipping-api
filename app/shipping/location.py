"""
Locational functions and services for shipping.
"""
import warnings
from geopy.geocoders import GoogleV3
import sys
from os import environ

warehouse_api_key = environ.get("MAPS_API_KEY")
if (warehouse_api_key is None and "pytest" not in sys.modules):
    warnings.warn("No API key provided for the warehouse API. Some functionality may be limited.")

geolocator: GoogleV3 | None = GoogleV3(api_key=warehouse_api_key) if warehouse_api_key is not None else None


def get_address_coordinates(address: str) -> tuple[float, float]:
    """
    Get the coordinates for a given address.

    :param address: the address to get the coordinates for
    :return: the coordinates for the address
    """
    if geolocator is None:
        return (34.992180, -78.137839)
    else:
        location = geolocator.geocode(components={"country": "US", "address": address})
        return (location.latitude, location.longitude)
