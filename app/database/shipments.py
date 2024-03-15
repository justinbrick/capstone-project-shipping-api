from uuid import UUID
from ..database import connection
from ..models.shipment import Shipment, ShipmentStatus
from ..database import ColumnNotFoundException, ColumnInsertionException
from sqlite3 import OperationalError

# Drop shipment table
connection.execute("DROP TABLE IF EXISTS shipments")

# Drop shipment status table
connection.execute("DROP TABLE IF EXISTS shipment_status")

connection.execute("""
CREATE TABLE IF NOT EXISTS shipments (
                   shipment_id TEXT PRIMARY KEY,
                   order_id TEXT,
                   shipping_address TEXT,
                   provider TEXT,
                   provider_shipment_id TEXT
)
""")

connection.execute("""
CREATE TABLE IF NOT EXISTS shipment_status (
                   shipment_id TEXT PRIMARY KEY,
                   status_message TEXT
)                   
""")


def save_shipment(shipment: Shipment) -> None:
    """
    Save the shipment to the database.
    """
    try:
        connection.execute("INSERT INTO shipments (shipment_id, order_id, shipping_address, provider, provider_shipment_id) VALUES (?, ?, ?, ?, ?)", (str(shipment.shipment_id), str(shipment.order_id), shipment.shipping_address, shipment.provider, shipment.provider_shipment_id))
    except OperationalError:
        raise ColumnInsertionException("Could not commit data to the database!")

def get_shipment(shipment_id: UUID) -> Shipment:
    """
    Get the shipment from the database, using the shipment ID.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM shipments WHERE shipment_id=?", (str(shipment_id),))
    shipment_row = cursor.fetchone()
    if (shipment_row is None or len(shipment_row) == 0):
        raise ColumnNotFoundException(f"Could not get a shipment @ \"{shipment_id}\"")
    return Shipment(shipment_id=shipment_row[0], order_id=shipment_row[1], shipping_address=shipment_row[2], provider=shipment_row[3], provider_shipment_id=shipment_row[4])

def get_shipment_status(shipment_id: UUID) -> ShipmentStatus:
    """
    Get the status for a shipment, given a shipment ID.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM shipment_status WHERE shipment_id=?", (str(shipment_id),))
    status_row = cursor.fetchone()
    if (status_row is None or len(status_row) == 0):
        raise ColumnNotFoundException(f"Could not get shipment status @ \"{shipment_id}\"")
    return ShipmentStatus(order_id=status_row[0], status=status_row[1])