"""
The module which contains helper functions for authentication and authorization.
"""

from os import environ

# The tenant ID of the Azure AD tenant.
TENANT_ID = environ.get("TENANT_ID")
if TENANT_ID is None:
    raise ValueError("TENANT_ID is not set.")
# The short name (used in {shortname}.onmicrosoft.com) of the tenant.
TENANT_SHORT_NAME = environ.get("TENANT_SHORT_NAME")
if TENANT_SHORT_NAME is None:
    raise ValueError("TENANT_SHORT_NAME is not set.")
# This is the user flow that is used for the user login.
USER_FLOW = environ.get("USER_FLOW")
if USER_FLOW is None:
    raise ValueError("USER_FLOW is not set.")
# The client ID of the Azure AD application. This is the the API!! application ID. Do not use the mobile application ID.
# This also doubles as the audience for the token.
CLIENT_ID = environ.get("CLIENT_ID")
if CLIENT_ID is None:
    raise ValueError("CLIENT_ID is not set.")
# The client secret of the Azure AD application.
CLIENT_SECRET = environ.get("CLIENT_SECRET")
if CLIENT_SECRET is None:
    raise ValueError("CLIENT_SECRET is not set.")
