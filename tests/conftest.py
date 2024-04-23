"""
Configuration file for pytest.
"""

__author__ = "Justin B. (justin@justin.directory)"

# pylint: disable=W0621

import os
from datetime import datetime, timedelta
from random import choice, randint
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

test_addresses = [
    "1790 Quarry Rd, Winston-Salem, NC 27107",
    "196 NC-801, Bermuda Run, NC 27006",
    "Palmyra Rd, Clarksville, TN 37191",
    "1709 S E St, Broken Bow, NE 68822",
    "CA-44, Susanville, CA 96130",
    "1461 Magnolia Blvd W, Seattle, WA 98199",
    "6320 Bandera Rd, Leon Valley, TX 78238",
    "4995 Gardenia St, Clay Springs, AZ 85923",
    "1650 Premium Outlet Blvd, Aurora, IL 60502",
    "821 Waterville Rd, Skowhegan, ME 04976"
]

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
    for i in range(1, 30):
        test_items.append(WarehouseItem(
            warehouse_id=warehouse.warehouse_id, upc=i, stock=10))

provider_list = list(Provider)


def generate_mock_shipment_items() -> list[ShipmentItem]:
    return [
        ShipmentItem(
            upc=i-2,
            stock=randint(5, 10)
        ) for i in range(randint(3, 10))
    ]


def generate_mock_shipment_status() -> ShipmentStatus:
    return ShipmentStatus(
        message=Status.PENDING,
        expected_at=datetime.now()+timedelta(days=3),
        updated_at=datetime.now(),
        delivered_at=None
    )


def generate_mock_shipments() -> list[Shipment]:
    return [
        Shipment(
            shipment_id=uuid4(),
            shipping_address=choice(test_addresses),
            from_address=choice(test_warehouses).address,
            provider=provider_list[i % len(provider_list)],
            provider_shipment_id=str(uuid4()),
            created_at=datetime.now() - timedelta(hours=randint(10, 20)),
            status=generate_mock_shipment_status(),
            items=generate_mock_shipment_items()
        ) for i in range(12)
    ]


def generate_mock_deliveries() -> list[Delivery]:
    return [
        Delivery(
            delivery_id=uuid4(),
            created_at=datetime.now(),
            fulfilled_at=None,
            delivery_sla=choice(list(SLA)),
            recipient_address=choice(test_addresses),
            shipments=generate_mock_shipments()
        )
    ]


def generate_mock_orders() -> list[Order]:
    return [
        Order(
            order_id=uuid4(),
            customer_id=uuid4(),
            created_at=datetime.now() - timedelta(hours=randint(2, 500)),
            deliveries=generate_mock_deliveries()
        ) for _ in range(10)
    ]


mock_orders = [
    Order(
        order_id=uuid4(),
        customer_id=mock_user_id,
        created_at=datetime.now(),
        deliveries=[
            Delivery(
                delivery_id=uuid4(),
                created_at=datetime.now(),
                fulfilled_at=None,
                delivery_sla=choice(list(SLA)),
                recipient_address="2683 NC-24, Warsaw, NC 28398",
                shipments=[
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
            )
        ]
    ),
]

if os.environ.get("TEST_FRONTLOAD", None) is not None:
    for order in generate_mock_orders():
        mock_orders.append(order)

mock_order_id = mock_orders[0].order_id
mock_delivery_id = mock_orders[0].deliveries[0].delivery_id
mock_shipment_id = mock_orders[0].deliveries[0].shipments[0].shipment_id


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
    session.add_all(mock_orders)
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
