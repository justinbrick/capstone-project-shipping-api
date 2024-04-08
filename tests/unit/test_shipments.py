"""
Unit tests for the shipments module.
"""

from uuid import uuid4
from random import choice, randint

import pytest
from app.routers.orders import create_order_delivery
from app.shipping.enums import SLA
import tests.conftest

from app.inventory.warehouse import get_nearest_warehouses
from app.shipping.models import CreateDeliveryRequest, CreateShipmentRequest, Provider, ShipmentItem


random_streets = [
    "Pilsbury Doughboy Lane",
    "Sesame Street",
    "Elm Street",
    "Baker Street",
    "Wallaby Way",
    "Infinity Loop"
]


def gen_random_address() -> str:
    return f"{randint(1, 1000)} {choice(random_streets)}"


def gen_fake_shipment_request() -> CreateShipmentRequest:
    return CreateShipmentRequest(
        from_address=gen_random_address(),
        shipping_address=gen_random_address(),
        provider=choice(list(Provider)),
        items=[]
    )


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
    assert delivery.fulfilled_at is None


@pytest.mark.asyncio
async def test_get_nearest_warehouses(db):
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
