
"""
Authentication & Authorization Middleware
"""

__author__ = "Justin B. (justin@justin.directory)"


from typing import Optional

import jwt
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from jwt.algorithms import RSAAlgorithm
from starlette.datastructures import URL, Headers
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.auth.microsoft import get_json_keys
from app.auth.profile import AccountProfile

# Some warnings for debug mode, as we are not verifying the token.
if __debug__:
    import warnings
    warnings.warn("Debug mode is enabled. Tokens are not being verified.")
    print("WARNING: Debug mode is enabled. Tokens are not being verified.")
    print("WARNING: This is a security risk and should not be used in production.")
    print("WARNING: To disable debug mode, run the application with the -O flag.")


class EntraOAuth2Middleware:
    """
    Pure ASGI Middleware that verifies the token before proceeding.
    After proper verification, it adds the JWT to the scope.

    :param app: The ASGI application to wrap around.
    :param tenant_id: The tenant ID to verify the token against.
    :param client_id: The client ID of this API application.
    :param anonymous_endpoints: A list of endpoints that do not require authentication.

    """

    def __init__(self, app: ASGIApp, tenant_id: str, client_id: str, b2c_short_name: str, anonymous_endpoints: Optional[list[str]] = None) -> None:
        self.app = app
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.issuer_url = f"https://{b2c_short_name}.b2clogin.com/{tenant_id}/v2.0/"

        if anonymous_endpoints is None:
            anonymous_endpoints = []

        self.anonymous_endpoints = anonymous_endpoints

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        url = URL(scope=scope)

        # If the URL is in the anonymous endpoints, we don't need to authenticate.
        if url.path in self.anonymous_endpoints:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        # Get the authorization as a bearer token, throw authorization error if it doesn't.
        authorization = headers.get("authorization")
        if authorization is None:
            response = PlainTextResponse(
                "Authorization header is required.", status_code=401)
            await response(scope, receive, send)
            return

        # Get the token from the authorization header, verify it is bearer token.
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            response = PlainTextResponse(
                "Invalid authorization header.", status_code=401)
            await response(scope, receive, send)
            return

        # Get the bearer token, verify it is valid.
        token = parts[1]
        try:
            if __debug__:
                # If we are in debug mode, we can skip the verification of the token.
                options = {
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_aud": False,
                    "verify_iss": False,
                    "verify_sub": False,
                    "verify_jti": False
                }
                debug_jwt = jwt.decode(token, options=options)
                scope["b2c_profile"] = AccountProfile(debug_jwt)
                await self.app(scope, receive, send)
                return

            # Gets the first part of the JWT, so we can verify against the key ID (kid)
            jwt_keys = await get_json_keys()
            unverified_header = jwt.get_unverified_header(token)

            accepted_keys = [
                key for key in jwt_keys if key["kid"] == unverified_header["kid"]]
            if len(accepted_keys) == 0:
                response = PlainTextResponse(
                    "Invalid token - unsigned.", status_code=401)
                await response(scope, receive, send)
                return
            accepted_key = accepted_keys[0]

            # Convert accepted_key to PEM format
            reformed_key = RSAAlgorithm.from_jwk(accepted_key).public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.PKCS1
            )

            # What to verify, everything by default should be true, but these are manually set just in case.
            options = {"verify_exp": True, "verify_signature": True}

            # Decoding into the JWT payload
            payload = jwt.decode(
                token,
                reformed_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer_url,
                options=options
            )

            # Hooray, they've passed verification!
            profile = AccountProfile(payload)
            scope["b2c_profile"] = profile
            await self.app(scope, receive, send)
        except jwt.DecodeError:
            response = PlainTextResponse("Invalid token.", status_code=401)
            await response(scope, receive, send)
            return
        except jwt.ExpiredSignatureError:
            response = PlainTextResponse("Token has expired.", status_code=401)
            await response(scope, receive, send)
            return
        except jwt.InvalidTokenError as e:
            response = PlainTextResponse("Invalid token.", status_code=401)
            await response(scope, receive, send)
            return
        except jwt.PyJWTError as exc:
            if __debug__:
                print("An error occurred while verifying the token: ", exc)

            response = PlainTextResponse("Invalid token.", status_code=401)
            await response(scope, receive, send)
            return
