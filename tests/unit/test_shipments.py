"""
Unit tests for the shipments module.
"""

__author__ = "Justin B. (justin@justin.directory)"

from uuid import UUID

import pytest
from sqlalchemy.orm.session import Session
from app.auth.profile import AccountProfile
from app.parameters.shipment import FullShipmentQueryParams
from app.routers.shipments import (get_shipment, get_shipments,
                                   update_shipment_status)
from app.shipping.providers import ShipmentProvider
from app.shipping.enums import Status
from app.shipping.models import ShipmentStatusPatchRequest


@pytest.mark.asyncio
async def test_get_shipment(session: Session, shipment_id: UUID):
    """
    Tests the retrieval of a shipment.
    """
    shipment = await get_shipment(shipment_id, session)
    assert shipment is not None
    assert shipment.shipment_id == shipment_id


@pytest.mark.asyncio
async def test_get_shipments(session: Session):
    """
    Tests the retrieval of all shipments.
    """
    shipment_query = FullShipmentQueryParams()
    shipments = await get_shipments(shipment_query, session)
    assert len(shipments) == 2


@pytest.mark.asyncio
async def test_get_shipments_from_partial_delivery_id(delivery_id: UUID, session: Session):
    """
    Test a partial shipment query, with the delivery ID filled in.
    """
    shipment_query = FullShipmentQueryParams(delivery_id=str(delivery_id)[:5])
    shipments = await get_shipments(shipment_query, session)
    assert len(shipments) == 2


@pytest.mark.asyncio
async def test_get_shipments_from_invalid_delivery_id(session: Session):
    """
    Create a shipment query with an invalid delivery ID.
    """
    shipment_query = FullShipmentQueryParams(delivery_id="invalid")
    shipments = await get_shipments(shipment_query, session)
    assert len(shipments) == 0


@pytest.mark.asyncio
async def test_update_shipment_status(shipment_id: UUID, session: Session, account: AccountProfile):
    """
    Test updating the shipment status.
    """
    # TODO: Needs get_shipment_status to be implemented on shipment providers.
    shipment = await ShipmentProvider.get_shipment_status(shipment_id, session)
    assert shipment.status == "PENDING"

    new_status = ShipmentStatusPatchRequest(
        message=Status.SHIPPED
    )
    status = await update_shipment_status(shipment_id, new_status, session, account)
    assert status.message == Status.SHIPPED
