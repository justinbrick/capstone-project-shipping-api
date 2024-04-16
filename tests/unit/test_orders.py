"""
Test order-related router requests.
"""

__author__ = "Justin B. (justin@justin.directory)"


from app.routers.orders import create_order_delivery, create_order_return
from app.shipping.enums import SLA
from app.shipping.models import CreateDeliveryRequest, CreateReturnRequest, ShipmentItem


import pytest
from sqlalchemy.orm.session import Session


from uuid import uuid4


@pytest.mark.asyncio
async def test_create_delivery(session: Session):
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
async def test_create_return(session: Session):
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
