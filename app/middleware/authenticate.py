
"""
Authentication & Authorization Middleware
"""

from fastapi import Depends, Request, HTTPException
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.datastructures import Headers, URL
from starlette.responses import PlainTextResponse
import inspect
import jwt
from jwt.algorithms import RSAAlgorithm
# import JWT encoding enums
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from app.auth.microsoft import get_json_keys, get_user_json_keys


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


def __get_jwt(request: Request):
    """
    Gets the JWT of the access token from the request.
    """
    jwt = request.scope["jwt"]
    if jwt is None:
        raise ValueError("JWT is required for this request.")
    yield jwt


def require_scopes(scope: str):
    """
    A decorator that requires a specific scope to be present in the JWT.

    """

    if scope is None or len(scope) == 0:
        raise ValueError("Scopes are required for this decorator.")

    def decorator(func):
        func_signature = inspect.signature(func)
        replaced_parameters = [
            *func_signature.parameters.values(),
            inspect.Parameter("jwt", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=Depends(__get_jwt)),
        ]

        async def wrapper(*args, jwt: any = Depends(__get_jwt), **kwargs):
            scope_string = jwt["scp"]

            # Check scopes
            if scope_string is None:
                raise HTTPException(status_code=401, detail="Invalid scope.")
            if scope not in scope_string:
                raise HTTPException(status_code=401, detail="Invalid scope.")

            return await func(*args, **kwargs)

        wrapper.__signature__ = func_signature.replace(parameters=replaced_parameters)
        __copy_func_meta(wrapper, func)
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
            response = PlainTextResponse("Authorization header is required.", status_code=401)
            await response(scope, receive, send)
            return
    
        # Get the token from the authorization header, verify it is bearer token.
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            response = PlainTextResponse("Invalid authorization header.", status_code=401)
            await response(scope, receive, send)
            return
        
        # Get the bearer token, verify it is valid.
        token = parts[1]
        try:
            # Gets the first part of the JWT, so we can verify against the key ID (kid)
            jwt_keys = await get_user_json_keys()
            unverified_header = jwt.get_unverified_header(token)

            accepted_keys = [key for key in jwt_keys if key["kid"] == unverified_header["kid"]]
            if len(accepted_keys) == 0:
                response = PlainTextResponse("Invalid token - unsigned.", status_code=401)
                await response(scope, receive, send)
                return
            accepted_key = accepted_keys[0]

            # Convert accepted_key to PEM format
            reformed_key = RSAAlgorithm.from_jwk(accepted_key).public_bytes(encoding=Encoding.PEM, format=PublicFormat.PKCS1)

            # You can optionally choose to verify the issuer to be the B2C issuer, or classic sts issuer.
            # TODO: Implement this logic. Low priority. I think? Needs research. Already seems overkill anyway.
            payload = jwt.decode(token, reformed_key, algorithms=["RS256"], audience=self.client_id, verify=True)
            # Hooray, they've passed verification!
            scope["jwt"] = payload
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
        except Exception as exc:
            response = PlainTextResponse("Invalid token.", status_code=401)
            await response(scope, receive, send)
            return