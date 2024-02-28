from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid

from .connection import Base

class Shipment(Base):
    """
    An ORM model representing a shipment in the database.
    """
    __tablename__ = "shipments"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[UUID] = relationship(ForeignKey("orders.id"))


