"""
A pagination parameter is needed to limit the number of results returned by the API.
"""

__author__ = "Justin B. (justin@justin.directory)"

from pydantic import BaseModel


class PaginationParams(BaseModel):
    """
    Parameters for pagination.
    """
    limit: int = 50
    offset: int = 0
