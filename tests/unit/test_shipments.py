"""
Unit tests for the shipments module.
"""

from uuid import uuid4
from random import choice, randint

import pytest
from app.routers.deliveries import make_delivery_breakdown
from app.routers.orders import create_order_delivery, create_order_return
from app.shipping.enums import SLA
import tests.conftest

from app.inventory.warehouse import get_nearest_warehouses
from app.shipping.models import CreateDeliveryRequest, CreateReturnRequest, CreateShipmentRequest, Provider, ShipmentItem


@pytest.mark.asyncio
async def test_create_delivery_breakdown(session):
    """
    Tests the creation of a delivery breakdown.
    """
    request = CreateDeliveryRequest(
        delivery_sla=SLA.STANDARD,
        items=[
            ShipmentItem(upc=1, stock=9),
            ShipmentItem(upc=2, stock=12)
        ],
        recipient_address="2683 NC-24, Warsaw, NC 28398"
    )

    delivery_breakdown = await make_delivery_breakdown(request)
    assert delivery_breakdown.recipient_address == request.recipient_address
    assert delivery_breakdown.expected_at is not None
    assert delivery_breakdown.can_meet_sla is True
    assert len(delivery_breakdown.delivery_times) == 2


@pytest.mark.asyncio
async def test_create_delivery(session):
    """
    Tests the creation of a shipment.
    """
    order_id = uuid4()
    request = CreateDeliveryRequest(
        delivery_sla=SLA.STANDARD,
        items=[
            ShipmentItem(upc=1, stock=9),
            ShipmentItem(upc=2, stock=12)
        ],
        recipient_address="2683 NC-24, Warsaw, NC 28398"
    )

    delivery = await create_order_delivery(order_id, request, session)
    assert delivery.order_id == order_id
    assert delivery.delivery_sla == request.delivery_sla
    assert len(delivery.shipments) == 2
    assert delivery.created_at is not None


@pytest.mark.asyncio
async def test_create_return(session):
    order_id = uuid4()
    request = CreateReturnRequest(
        order_id=order_id,
        items=[
            ShipmentItem(upc=1, stock=9),
            ShipmentItem(upc=2, stock=12)
        ],
        from_address="2683 NC-24, Warsaw, NC 28398"
    )
    order_return = await create_order_return(order_id, request, session)
    assert order_return.order_id == order_id
    assert order_return.created_at is not None


@pytest.mark.asyncio
async def test_get_nearest_warehouses():
    """
    Tests a known location to ensure the nearest warehouses are returned.
    """

    test_address = "2683 NC-24, Warsaw, NC 28398"
    nearest_warehouses = await get_nearest_warehouses(test_address)
    assert len(nearest_warehouses) == 4
    assert nearest_warehouses[0].address == "279 Kadire Dr, Marion, NC 28752"
    assert nearest_warehouses[1].address == "131 E Exchange Ave, Fort Worth, TX 76164"
    assert nearest_warehouses[2].address == "409 N 10th St, New Salem, ND 58563"
    assert nearest_warehouses[3].address == "1540 Navco Ln, Wells, NV 89835"
