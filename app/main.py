"""
The main module, containing the FastAPI application.
"""

__author__ = "Justin B. (justin@justin.directory)"


from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse

from app.auth import CLIENT_ID, TENANT_ID
from app.auth.dependencies import has_roles
from app.database import engine
from app.database.schemas import Base
from app.middleware.authenticate import EntraOAuth2Middleware
from app.routers import internal, me, orders, returns, shipments, users

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


if __name__ == "__main__":
    from os import environ

    import uvicorn
    host_name = environ.get("HOST_NAME", "127.0.0.1")
    host_port = int(environ.get("HOST_PORT", "8000"))
    uvicorn.run(app, host=host_name, port=host_port)
