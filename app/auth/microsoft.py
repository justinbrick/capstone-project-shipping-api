"""
Microsoft-based auth information
"""

__author__ = "Justin B. (justin@justin.directory)"

from datetime import datetime, timedelta
from typing import Optional
import httpx

from . import TENANT_SHORT_NAME, USER_FLOW

_user_client = httpx.AsyncClient(
    base_url=f"https://{TENANT_SHORT_NAME}.b2clogin.com")

_last_checked: Optional[datetime] = datetime.now() - timedelta(minutes=5)
_cached_keys: list[dict] = []


async def get_json_keys() -> list[dict]:
    """
    Get all the JWKs for a tenant under the B2C issuer.
    This is used for user logins.
    """

    if _last_checked + timedelta(minutes=5) > datetime.now():
        return _cached_keys

    response = await _user_client.get(f"/{TENANT_SHORT_NAME}.onmicrosoft.com/discovery/v2.0/keys?p=b2c_1_{USER_FLOW}")
    response.raise_for_status()

    _last_checked = datetime.now()
    _cached_keys = response.json()["keys"]

    return _cached_keys
