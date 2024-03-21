"""
File containing methods for tracking a shipment
"""

from ..models.shipment import ShipmentStatus


async def get_shipment_status(shipment_id: str) -> ShipmentStatus:
    """
    STUB
    Get the shipment status for a specific shipment ID.
    Due to varying providers, this is a delegate request.
    As a result, it is volatile depending on the provider.
    """
