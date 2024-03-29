"""
Unit tests for the shipments module.
"""

from uuid import uuid4
from random import choice, randint

import pytest

from app.database.schemas import Warehouse
from app.database.warehouse import get_nearest_warehouse
from app.models.shipment import CreateShipmentRequest, Provider
from app.database.shipments import create_shipment, get_shipment
from app import get_db

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
        order_id=uuid4(),
        shipping_address=gen_random_address(),
        provider=choice(list(Provider))
    )


@pytest.mark.dependency()
def test_create_shipment():
    """
    Test the creation of a shipment, given fake data.
    """
    db = next(get_db())
    request = gen_fake_shipment_request()
    shipment = create_shipment(db, request)
    assert shipment.order_id == request.order_id
    assert shipment.shipping_address == request.shipping_address
    assert shipment.provider == request.provider
    assert shipment.shipment_id is not None


@pytest.mark.dependency(depends=["test_create_shipment"])
def test_get_shipment():
    """
    Test the retrieval of a shipment using data that has already been put into the database.
    """
    db = next(get_db())
    request = gen_fake_shipment_request()
    shipment = create_shipment(db, request)
    retrieved_shipment = get_shipment(db, shipment.shipment_id)
    assert retrieved_shipment == shipment
    assert retrieved_shipment.shipment_id == shipment.shipment_id
    assert retrieved_shipment.order_id == shipment.order_id
    assert retrieved_shipment.shipping_address == shipment.shipping_address
    assert retrieved_shipment.provider == shipment.provider
    assert retrieved_shipment.created_at == shipment.created_at
    assert retrieved_shipment.provider_shipment_id == shipment.provider_shipment_id


test_warehouses = [
    Warehouse(warehouse_id=uuid4(), address="East", latitude=35.705054, longitude=-79.809727),
    Warehouse(warehouse_id=uuid4(), address="South", latitude=31.193425, longitude=-98.624873),
    Warehouse(warehouse_id=uuid4(), address="West", latitude=41.130868, longitude=-115.962108),
    Warehouse(warehouse_id=uuid4(), address="North", latitude=45.379562, longitude=-98.490035)
]


def test_get_nearest_warehouse():
    """
    Tests a known location to ensure the nearest warehouse is returned.
    """
    db = next(get_db())
    db.add_all(test_warehouses)
    db.commit()
    test_address = "2683 NC-24, Warsaw, NC 28398"
    nearest_warehouse = get_nearest_warehouse(db, test_address)
    assert nearest_warehouse.address == "East"
