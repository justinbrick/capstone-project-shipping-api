"""
The main module, containing the FastAPI application.
"""

__author__ = "Justin B. (justin@justin.directory)"

from os import environ

from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi

from app.auth import CLIENT_ID, TENANT_ID
from app.auth.dependencies import has_roles
from app.database import engine
from app.database.schemas import Base
from app.middleware.authenticate import EntraOAuth2Middleware
from app.routers import internal, me, orders, returns, shipments, users


SERVER_URL = environ.get("SERVER_URL", "http://127.0.0.1:8000")

# Create all the tables mentioned in this schema.
Base.metadata.create_all(bind=engine)


app = FastAPI()

# Middleware
anonymous_endpoints = ["/docs", "/openapi.json", "/about"]
app.add_middleware(EntraOAuth2Middleware, client_id=CLIENT_ID,
                   tenant_id=TENANT_ID, anonymous_endpoints=anonymous_endpoints)

# Routers
app.include_router(
    shipments.router,
    prefix="/shipments",
    tags=["shipments"],
    dependencies=[
        Depends(has_roles(["SHP-STF"]))
    ]
)
app.include_router(
    internal.router,
    prefix="/internal",
    tags=["internal"],
    dependencies=[
        Depends(has_roles(["SHP-DLR"]))
    ]
)
app.include_router(me.router, prefix="/me", tags=["me"])
app.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    dependencies=[
        Depends(has_roles(["SHP-STF"]))
    ]
)
app.include_router(returns.router, prefix="/returns", tags=["returns"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])


@app.get("/about", response_class=HTMLResponse)
async def about() -> str:
    """
    Returns a simple HTML page with information about the API.
    """
    return "<!DOCTYPE html><html><body><h1>For security reasons, a website cannot be provided. Please use the mobile app.</h1></body></html>"


def openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="BitBuggy Shipping",
        version="2.0.1",
        openapi_version="3.0.3",
        summary="BitBuggy Shipping",
        description="Management of shipping and delivery information.",
        routes=app.routes,
        servers=[
            {
                "url": SERVER_URL,
                "description": "Shipping Server"
            }
        ]
    )

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = openapi

if __name__ == "__main__":
    from os import environ

    import uvicorn
    host_name = environ.get("HOST_NAME", "127.0.0.1")
    host_port = int(environ.get("HOST_PORT", "8000"))
    uvicorn.run(app, host=host_name, port=host_port)
