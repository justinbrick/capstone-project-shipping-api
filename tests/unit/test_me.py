"""
Unit tests for functions regarding the requesting user.
"""

__author__ = "Justin B. (justin@justin.directory)"


import pytest

from app.parameters.shipment import BaseShipmentQueryParams
from app.routers.me import get_my_deliveries, get_my_shipments


@pytest.mark.asyncio
async def test_get_my_shipments(session, account):
    """
    Tests the retrieval of all shipments.
    """
    params = BaseShipmentQueryParams()
    shipments = await get_my_shipments(params, account, session)
    assert len(shipments) == 2


@pytest.mark.asyncio
async def test_get_my_deliveries(session, account):
    """
    Tests the retrieval of all deliveries.
    """
    deliveries = await get_my_deliveries(session, account)
    assert len(deliveries) == 1

""" need shipment providers to implement get_shipment_status """
# @pytest.mark.asyncio
# async def test_get_my_shipment_status(session, account):
#     """
#     Tests the retrieval of a shipment status.
#     """
#     shipments = await get_my_shipments(session, account)
#     shipment_id = shipments[0].shipment_id
#     status = await get_my_shipment_status(shipment_id, session, account)
#     assert status is not None
