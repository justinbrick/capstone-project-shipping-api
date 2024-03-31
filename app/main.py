from fastapi import FastAPI

from .auth import CLIENT_ID, TENANT_ID
from .routers import shipments, users, returns
from .middleware.authenticate import EntraOAuth2Middleware
from .database import engine
from .database.schemas import Base

# Create all the tables mentioned in this schema.
Base.metadata.create_all(bind=engine)


app = FastAPI()

# Middleware
anonymous_endpoints = ["/docs", "/openapi.json"]
app.add_middleware(EntraOAuth2Middleware, client_id=CLIENT_ID, tenant_id=TENANT_ID, anonymous_endpoints=anonymous_endpoints)

# Routers
app.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(returns.router, prefix="/returns", tags=["returns"])

if __name__ == "__main__":
    import uvicorn
    from os import environ
    host_name = environ.get("HOST_NAME", "127.0.0.1")
    host_port = int(environ.get("HOST_PORT", "8000"))
    uvicorn.run(app, host=host_name, port=host_port)
