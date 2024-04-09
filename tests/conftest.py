from datetime import datetime, timedelta
import os
from random import choice
from uuid import uuid4
from dotenv import load_dotenv
import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker


from app.database.schemas import Delivery, Shipment, ShipmentDeliveryInfo, ShipmentItem, ShipmentStatus, Warehouse, WarehouseItem, Base
from app.database import engine, Session
from app.shipping.enums import SLA, Provider, Status


def pytest_configure(config):
    """
    Checks if test.db exists, and if it does, deletes it.
    Also loads .env file.
    """
    load_dotenv()

    if os.path.exists("test.db"):
        os.remove("test.db")


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


mock_delivery_id = uuid4()
mock_delivery_shipments = [
    Shipment(
        shipment_id=uuid4(),
        shipping_address="2683 NC-24, Warsaw, NC 28398",
        from_address=test_warehouses[0].address,
        provider=choice(list(Provider)),
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
mock_delivery = Delivery(
    delivery_id=mock_delivery_id,
    order_id=uuid4(),
    created_at=datetime.now(),
    fulfilled_at=None,
    delivery_sla=choice(list(SLA)),
    recipient_address="2683 NC-24, Warsaw, NC 28398",
    delivery_shipments=[
        ShipmentDeliveryInfo(
            shipment_id=shipment.shipment_id,
            shipment=shipment,
            delivery_id=mock_delivery_id
        ) for shipment in mock_delivery_shipments
    ]

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
    session.add(mock_delivery)
    session.commit()
    session.close()
    yield


@pytest.fixture(scope="session")
def delivery_id():
    return mock_delivery_id


@pytest.fixture(scope="session")
def shipment_id():
    return mock_delivery_shipments[0].shipment_id


@pytest.fixture(scope="function")
def session(db):
    """
    Returns a database session.
    """
    session_factory = sessionmaker(bind=db)
    session = session_factory()
    yield session
    session.close()
