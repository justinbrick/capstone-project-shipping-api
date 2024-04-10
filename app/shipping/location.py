"""
Locational functions and services for shipping.
"""

__author__ = "Justin B. (justin@justin.directory)"


import warnings
from async_lru import alru_cache
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import GoogleV3, Photon
import sys
from os import environ

"""
Caching for address coordinates is a relatively small number.
This is because the coordinates will be queried in a quick burst.
For debug purposes, the cache size is unlimited, as it will return random values.
"""
warehouse_api_key = environ.get("MAPS_API_KEY")

if warehouse_api_key is None:
    warnings.warn(
        "Could not find Google Maps API key. Geocoding will be done through Photon.")
    print("WARNING: Photon geocoding is prone to errors & rate limiting.")
    print("WARNING: To disable debug mode, run the application with the -O flag.")

cache_size = 128
if __debug__:
    cache_size = None


@alru_cache(maxsize=cache_size)
async def get_address_coordinates(address: str) -> tuple[float, float]:
    """
    Get the coordinates for a given address.

    :param address: the address to get the coordinates for
    :return: the coordinates for the address
    """
    if warehouse_api_key is None:
        async with Photon(adapter_factory=AioHTTPAdapter) as photon:
            location = await photon.geocode(address)
            return (location.latitude, location.longitude)
    else:
        async with GoogleV3(api_key=warehouse_api_key, adapter_factory=AioHTTPAdapter) as google:
            location = await google.geocode(address)
            return (location.latitude, location.longitude)
