"""
A pagination parameter is needed to limit the number of results returned by the API.
"""


from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Query

from app import get_db


class PaginationParams(BaseModel):
    """
    Parameters for pagination.
    """
    limit: int = 50
    offset: int = 0
