import os
from uuid import uuid4
from dotenv import load_dotenv
import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker


from app.database.schemas import Delivery, Warehouse, WarehouseItem, Base
from app.database import engine, Session


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
    session.commit()
    session.close()
    yield


@pytest.fixture(scope="function")
def session(db):
    """
    Returns a database session.
    """
    session_factory = sessionmaker(bind=db)
    session = session_factory()
    yield session
    session.close()
