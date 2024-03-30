"""
Microsoft-based auth information
"""

import httpx

from . import TENANT_ID, TENANT_SHORT_NAME, USER_FLOW

_internal_client = httpx.AsyncClient(base_url="https://login.microsoftonline.com")
_user_client = httpx.AsyncClient(base_url=f"https://{TENANT_SHORT_NAME}.b2clogin.com")


async def get_json_keys() -> list[dict]:
    """
    Get all the JWKs for a tenant.
    :param tenant_id: The tenant ID to get the keys for.
    """
    response = await _internal_client.get(f"/{TENANT_ID}/discovery/v2.0/keys")
    response.raise_for_status()
    return response.json()["keys"]


async def get_user_json_keys() -> list[dict]:
    """
    Get all the JWKs for a tenant under the B2C issuer.
    This is used for user logins.
    """
    response = await _user_client.get(f"/{TENANT_SHORT_NAME}.onmicrosoft.com/discovery/v2.0/keys?p=b2c_1_{USER_FLOW}")
    response.raise_for_status()
    return response.json()["keys"]
