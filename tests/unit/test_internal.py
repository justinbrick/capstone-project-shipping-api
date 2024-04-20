"""
Tests for the internal router
"""

__author__ = "Justin B. (justin@justin.directory)"

import pytest

from app.parameters.pagination import PaginationParams
from app.routers.internal import get_open_shipments


@pytest.mark.asyncio
async def test_get_open_internal_shipments(session):
    """
    Tests the retrieval of all internal shipments.
    """
    params = PaginationParams()
    open_shipments = await get_open_shipments(params, session)

    assert len(open_shipments) == 1
