"""
Testing the users router
"""

__author__ = "Justin B. (justin@justin.directory)"

from uuid import UUID, uuid4
from fastapi import HTTPException
import pytest
from sqlalchemy.orm import Session

from app.auth.profile import AccountProfile
from app.parameters.shipment import BaseShipmentQueryParams
from app.routers.users import get_user_shipment, get_user_shipments


@pytest.mark.asyncio
async def test_get_user_shipments(account: AccountProfile, session: Session):
    """
    Test the get_user_shipments function
    """
    params = BaseShipmentQueryParams()
    shipments = await get_user_shipments(account.user_id, params, session)
    assert len(shipments) != 0


@pytest.mark.asyncio
async def test_get_user_shipment(account: AccountProfile, shipment_id: UUID, session: Session):
    """
    Test the get_user_shipment function
    """
    shipment = await get_user_shipment(account.user_id, shipment_id, session)
    assert shipment is not None
    assert shipment.shipment_id == shipment_id


@pytest.mark.asyncio
async def test_get_invalid_user_shipment(account: AccountProfile, session: Session):
    """
    Test the get_user_shipment function with an invalid shipment ID
    """
    bad_shipment_id = uuid4()
    try:
        await get_user_shipment(account.user_id, bad_shipment_id, session)
        assert False
    except HTTPException as e:
        assert e.status_code == 404
