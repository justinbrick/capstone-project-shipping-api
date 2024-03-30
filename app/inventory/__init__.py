"""
The inventory package contains the API for managing inventory of warehouses.
"""

from os import environ
import httpx
from msal import ConfidentialClientApplication
from ..auth import CLIENT_ID, TENANT_ID, TENANT_SHORT_NAME, CLIENT_SECRET

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = environ.get("INVENTORY_ACCESS_TOKEN")

msal_client = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority="https://bitbuggy.b2clogin.com/tfp/bitbuggy.onmicrosoft.com/B2C_1_BitBuggyLogin"
)


async def get_access_token(request):
    result = msal_client.acquire_token_for_client(scopes=["https://bitbuggy.dev/test-unused/.default"])
    print(result)
    print("ok")
    request.headers["Authorization"] = f"Bearer {result['access_token']}"

client = httpx.AsyncClient(base_url=BASE_URL, event_hooks={"request": [get_access_token]})
