from fastapi import FastAPI

from .routers import shipments
from .database import engine
from .database.schemas import Base

# Create all the tables mentioned in this schema.
Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
