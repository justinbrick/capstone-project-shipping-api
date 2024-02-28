
from sqlalchemy import UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
import uuid

from .connection import Base

class Order(Base):
    """
    An ORM model representing an order in the database.
    """
    __tablename__ = "orders"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
