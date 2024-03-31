"""
The inventory package contains the API for managing inventory of warehouses.
"""

from os import environ
import httpx
from ..auth import msal_client, TENANT_SHORT_NAME

BASE_URL = "http://localhost:8000"


async def get_access_token(request):
    result = msal_client.acquire_token_for_client(scopes=["https://bitbuggy.dev/test-unused/.default"])
    request.headers["Authorization"] = f"Bearer {result['access_token']}"

client = httpx.AsyncClient(base_url=BASE_URL, event_hooks={"request": [get_access_token]})
