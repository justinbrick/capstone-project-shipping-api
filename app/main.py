from fastapi import FastAPI

from .routers import shipments

app = FastAPI()

# If people want to get the OpenAPI documentation, then they can get it through this.
app.openapi_url = "/docs.json"

app.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
