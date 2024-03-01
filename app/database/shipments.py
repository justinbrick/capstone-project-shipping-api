from ..database import connection
from ..models.shipment import Shipment

connection.execute("DROP TABLE IF EXISTS shipments")

connection.execute("""
CREATE TABLE IF NOT EXISTS shipments (
                   shipment_id TEXT PRIMARY KEY,
                   order_id TEXT,
                   shipping_address TEXT,
                   provider TEXT,
                   provider_shipment_id TEXT
)
""")


def save_shipment(shipment: Shipment):
    """
    Save the shipment to the database.
    """
    connection.execute("INSERT INTO shipments (shipment_id, order_id, shipping_address, provider, provider_shipment_id) VALUES (?, ?, ?, ?, ?)", (str(shipment.shipment_id), str(shipment.order_id), shipment.shipping_address, shipment.provider, shipment.provider_shipment_id))
