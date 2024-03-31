"""
The module which contains helper functions for authentication and authorization.
"""

from os import environ
from msal import ConfidentialClientApplication


# The tenant ID of the Azure AD tenant.
TENANT_ID = environ.get("TENANT_ID")
# The short name (used in {shortname}.onmicrosoft.com) of the tenant.
TENANT_SHORT_NAME = environ.get("TENANT_SHORT_NAME")
# This is the user flow that is used for the user login.
USER_FLOW = environ.get("USER_FLOW")
# The client ID of the Azure AD application. This is the the API!! application ID. Do not use the mobile application ID.
# This also doubles as the audience for the token.
CLIENT_ID = environ.get("CLIENT_ID")
# The client secret of the Azure AD application.
CLIENT_SECRET = environ.get("CLIENT_SECRET")

if not __debug__:
    # Verify that the required environment variables are set.
    if CLIENT_SECRET is None:
        raise ValueError("CLIENT_SECRET is not set.")
    if CLIENT_ID is None:
        raise ValueError("CLIENT_ID is not set.")
    if TENANT_ID is None:
        raise ValueError("TENANT_ID is not set.")
    if USER_FLOW is None:
        raise ValueError("USER_FLOW is not set.")
    if TENANT_SHORT_NAME is None:
        raise ValueError("TENANT_SHORT_NAME is not set.")

msal_client = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=f"https://{TENANT_SHORT_NAME}.b2clogin.com/tfp/{TENANT_SHORT_NAME}.onmicrosoft.com/B2C_1_{USER_FLOW}"
)
