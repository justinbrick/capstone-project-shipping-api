"""
The inventory package contains the API for managing inventory of warehouses.
"""

from os import environ
import httpx

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = environ.get("INVENTORY_ACCESS_TOKEN")

client = httpx.AsyncClient(base_url=BASE_URL, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
