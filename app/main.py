from fastapi import FastAPI

from .routers import shipments
from .database import engine
from .database.schemas import Base

# Create all the tables mentioned in this schema.
Base.metadata.create_all(bind=engine)


app = FastAPI()

# If people want to get the OpenAPI documentation, then they can get it through this.
app.openapi_url = "/docs.json"

app.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
