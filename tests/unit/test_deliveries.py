import pytest

from app.inventory.warehouse import get_nearest_warehouses
from app.routers.deliveries import make_delivery_breakdown
from app.shipping.enums import SLA
from app.shipping.models import CreateDeliveryRequest, ShipmentItem


@pytest.mark.asyncio
async def test_make_delivery_breakdown():
    """
    Tests the creation of a delivery breakdown.
    """
    request = CreateDeliveryRequest(
        delivery_sla=SLA.STANDARD,
        items=[
            ShipmentItem(upc=3, stock=9),
            ShipmentItem(upc=4, stock=12)
        ],
        recipient_address="2683 NC-24, Warsaw, NC 28398"
    )

    delivery_breakdown = await make_delivery_breakdown(request)
    assert delivery_breakdown.recipient_address == request.recipient_address
    assert delivery_breakdown.expected_at is not None
    assert delivery_breakdown.can_meet_sla is True
    assert len(delivery_breakdown.delivery_times) == 2


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
