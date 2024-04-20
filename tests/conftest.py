"""
Configuration file for pytest.
"""

__author__ = "Justin B. (justin@justin.directory)"

# pylint: disable=W0621

import os
from datetime import datetime, timedelta
from random import choice
from uuid import UUID, uuid4

import pytest
from dotenv import load_dotenv
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.profile import AccountProfile
from app.database import engine
from app.database.schemas import (Base, Delivery, Order, Shipment,
                                  ShipmentItem, ShipmentStatus,
                                  ShippingEmployeeReservation, Warehouse,
                                  WarehouseItem)
from app.shipping.enums import SLA, Provider, Status


def pytest_configure(config):
    """
    Checks if test.db exists, and if it does, deletes it.
    Also loads .env file.
    """
    load_dotenv()

    if os.path.exists("test.db"):
        os.remove("test.db")


mock_user_id = UUID("722b0f37-fb56-477c-85ff-c4ef34bdd752")
# An unsigned test JWT, used for testing purposes.
jwt_content = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": int(datetime.now().timestamp()),
    "scp": "Shipment.Write Shipment.Read Shipment.Create",
    "extension_roles": "Admin,Test",
    "extension_uflag": True,
    "oid": str(mock_user_id)
}
account_profile = AccountProfile(jwt_content)

test_warehouses = [
    # East
    Warehouse(warehouse_id=uuid4(), address="279 Kadire Dr, Marion, NC 28752",
              latitude=35.705054, longitude=-79.809727),
    # South
    Warehouse(warehouse_id=uuid4(), address="131 E Exchange Ave, Fort Worth, TX 76164",
              latitude=31.193425, longitude=-98.624873),
    # West
    Warehouse(warehouse_id=uuid4(), address="1540 Navco Ln, Wells, NV 89835",
              latitude=41.130868, longitude=-115.962108),
    # North
    Warehouse(warehouse_id=uuid4(), address="409 N 10th St, New Salem, ND 58563",
              latitude=45.379562, longitude=-98.490035)
]

test_items: list[WarehouseItem] = []
for warehouse in test_warehouses:
    for i in range(1, 15):
        test_items.append(WarehouseItem(
            warehouse_id=warehouse.warehouse_id, upc=i, stock=10))


mock_order_id = uuid4()
mock_order = Order(
    order_id=mock_order_id,
    customer_id=mock_user_id,
    created_at=datetime.now()
)

mock_delivery_id = uuid4()
mock_delivery_shipments = [
    Shipment(
        shipment_id=uuid4(),
        shipping_address="2683 NC-24, Warsaw, NC 28398",
        from_address=test_warehouses[0].address,
        provider=Provider.INTERNAL,
        provider_shipment_id=str(uuid4()),
        created_at=datetime.now(),
        items=[
            ShipmentItem(upc=1, stock=9),
            ShipmentItem(upc=2, stock=12)
        ],
        status=ShipmentStatus(
            message=Status.PENDING,
            expected_at=datetime.now()+timedelta(days=3),
            updated_at=datetime.now(),
            delivered_at=None
        ),
        reservation=ShippingEmployeeReservation(
            employee_id=mock_user_id
        )
    ),
    Shipment(
        shipment_id=uuid4(),
        shipping_address="2683 NC-24, Warsaw, NC 28398",
        from_address=test_warehouses[0].address,
        provider=Provider.UPS,
        provider_shipment_id=str(uuid4()),
        created_at=datetime.now(),
        items=[
            ShipmentItem(upc=1, stock=9),
            ShipmentItem(upc=2, stock=12)
        ],
        status=ShipmentStatus(
            message=Status.PENDING,
            expected_at=datetime.now()+timedelta(days=3),
            updated_at=datetime.now(),
            delivered_at=None
        )
    )
]
mock_shipment_id = mock_delivery_shipments[0].shipment_id

mock_delivery = Delivery(
    delivery_id=mock_delivery_id,
    order_id=mock_order_id,
    created_at=datetime.now(),
    fulfilled_at=None,
    delivery_sla=choice(list(SLA)),
    recipient_address="2683 NC-24, Warsaw, NC 28398",
    shipments=mock_delivery_shipments
)


@pytest.fixture(scope="session")
def db():
    """
    Returns the database session.
    """
    return engine


@pytest.fixture(scope="session", autouse=True)
def setup_db(db: Engine):
    """
    Creates the tables in the database.
    """
    Base.metadata.create_all(db)
    session_factory = sessionmaker(bind=db)
    session = session_factory()
    session.add_all(test_warehouses)
    session.add_all(test_items)
    session.add(mock_order)
    session.add(mock_delivery)
    session.commit()
    session.close()
    yield


@pytest.fixture(scope="session")
def delivery_id():
    """
    Returns a delivery_id.
    """
    return mock_delivery_id


@pytest.fixture(scope="function")
def session(db: Engine):
    """
    Returns a database session.
    """
    connection = db.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def shipment_id() -> UUID:
    """
    Returns shipment_id.
    """
    return mock_shipment_id


@pytest.fixture(scope="function")
def account() -> AccountProfile:
    """
    Returns a mock account profile with certain claims.
    """
    return account_profile
