
"""
Authentication & Authorization Middleware
"""

__author__ = "Justin B. (justin@justin.directory)"

from typing import Optional
from fastapi import Depends, Request, HTTPException
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.datastructures import Headers, URL
from starlette.responses import PlainTextResponse
import inspect
import jwt
from jwt.algorithms import RSAAlgorithm
# import JWT encoding enums
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from app.auth.microsoft import get_json_keys
from app.auth import TENANT_SHORT_NAME
from app.auth.profile import AccountProfile

ISSUER_URL = f"https://{TENANT_SHORT_NAME}.b2clogin.com/{TENANT_SHORT_NAME}.onmicrosoft.com/v2.0"

# Some warnings for debug mode, as we are not verifying the token.
if __debug__:
    import warnings
    warnings.warn("Debug mode is enabled. Tokens are not being verified.")
    print("WARNING: Debug mode is enabled. Tokens are not being verified.")
    print("WARNING: This is a security risk and should not be used in production.")
    print("WARNING: To disable debug mode, run the application with the -O flag.")


class __INJECT_JWT:
    pass


def __copy_func_meta(to_func, from_func):
    """
    Copies the metadata from one function to another.
    This does not include the signature - only the annotations, name, and docstring.
    :param to_func: The function to copy the metadata to.
    :param from_func: The function to copy the metadata from.
    """
    to_func.__annotations__ = from_func.__annotations__
    to_func.__name__ = from_func.__name__
    to_func.__doc__ = from_func.__doc__


def __get_replaced_sig(signature: inspect.Signature, param_name: str) -> Optional[inspect.Signature]:
    """
    Adds a JWT parameter to the function signature.

    :param signature: The function signature to add the JWT parameter to.
    :param param_name: The name of the parameter to add.
    :return: The new function signature with the JWT parameter.
    """

    jwt_parameter = inspect.Parameter(
        param_name,
        inspect.Parameter.KEYWORD_ONLY,
        default=Depends(get_jwt),
        annotation=__INJECT_JWT
    )
    new_parameters = [
        *signature.parameters.values(),
        jwt_parameter
    ]

    return signature.replace(parameters=new_parameters)


def get_jwt(request: Request):
    """
    A dependency request, which gets the JWT from the current request scope.
    This takes advantage of FastAPI dependency injection.
    If you are not using FastAPI, then you must get the JWT from the ASGI request scope manually.
    """
    jwt = request.scope["jwt"]
    if jwt is None:
        raise HTTPException(status_code=401, detail="Invalid token.")
    yield jwt


def require_roles(roles: list[str]):
    """
    A decorator that requires a specific role to be present in the JWT.

    """
    if roles is None or len(roles) == 0:
        raise ValueError("Roles are required for this decorator.")

    def decorator(func):

        async def wrapper(*args, __bitbuggy_role_jwt: __INJECT_JWT = Depends(get_jwt), **kwargs):
            role_string = __bitbuggy_role_jwt["extension_roles"]

            # Check roles
            if role_string is None:
                raise HTTPException(status_code=403, detail="Invalid role.")
            if not any(role in role_string for role in roles):
                raise HTTPException(status_code=403, detail="Invalid role.")

            return await func(*args, **kwargs)

        replaced_signature = __get_replaced_sig(
            inspect.signature(func), "__bitbuggy_role_jwt")
        if replaced_signature is not None:
            wrapper.__signature__ = replaced_signature
        else:
            wrapper.__signature__ = inspect.signature(func)

        __copy_func_meta(wrapper, func)
        # Add the roles to the docstring.
        wrapper.__doc__ = f"{func.__doc__}\n\nRequires roles: {str.join(', ', roles)}"
        return wrapper
    return decorator


def require_scopes(scopes: list[str]):
    """
    A decorator that requires a specific scope to be present in the JWT.
    """

    if scopes is None or len(scopes) == 0:
        raise ValueError("Scopes are required for this decorator.")

    def decorator(func):

        async def wrapper(*args, __bitbuggy_scope_jwt: __INJECT_JWT = Depends(get_jwt), **kwargs):
            scope_string = __bitbuggy_scope_jwt["scp"]

            # Check scopes
            if scope_string is None:
                raise HTTPException(status_code=403, detail="Invalid scope.")
            if not all(scope in scope_string for scope in scopes):
                raise HTTPException(status_code=403, detail="Invalid scope.")

            return await func(*args, **kwargs)

        replaced_signature = __get_replaced_sig(
            inspect.signature(func), "__bitbuggy_scope_jwt")
        if replaced_signature is not None:
            wrapper.__signature__ = replaced_signature
        else:
            wrapper.__signature__ = inspect.signature(func)

        __copy_func_meta(wrapper, func)
        # Add the scopes to the docstring.
        wrapper.__doc__ = f"{func.__doc__}\n\nRequires scopes: {str.join(', ', scopes)}"
        return wrapper
    return decorator


class EntraOAuth2Middleware:
    """
    Pure ASGI Middleware that verifies the token before proceeding.
    After proper verification, it adds the JWT to the scope.

    :param app: The ASGI application to wrap around.
    :param tenant_id: The tenant ID to verify the token against.
    :param client_id: The client ID of this API application.
    :param anonymous_endpoints: A list of endpoints that do not require authentication.

    """

    def __init__(self, app: ASGIApp, tenant_id: str, client_id: str, anonymous_endpoints: list[str] = []) -> None:
        self.app = app
        self.tenant_id = tenant_id
        self.client_id = client_id
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
                scope["jwt"] = debug_jwt
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
                encoding=Encoding.PEM, format=PublicFormat.PKCS1)
            options = {"verify_exp": True, "verify_signature": True}
            payload = jwt.decode(token, reformed_key, algorithms=[
                                 "RS256"], audience=self.client_id, issuer=ISSUER_URL, options=options)
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
        except jwt.InvalidTokenError:
            response = PlainTextResponse("Invalid token.", status_code=401)
            await response(scope, receive, send)
            return
        except jwt.PyJWTError as exc:
            if __debug__:
                print("An error occurred while verifying the token: ", exc)

            response = PlainTextResponse("Invalid token.", status_code=401)
            await response(scope, receive, send)
            return
