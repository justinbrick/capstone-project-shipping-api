"""
In shipments, this contains functions used to get / modify shipments in our database.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..shipping.models import CreateShipmentRequest, ShipmentStatus
from ..shipping.enums import Provider
from . import schemas


def get_mock_shipping_status(db: Session, tracking_number: int) -> str:
    """
    Get the status of a package with a given tracking number.

    :param tracking_number: the tracking number to get the status for
    :return: the status of the package
    """
    shipment_status = db.query(schemas.ShipmentStatus).filter(
        schemas.ShipmentStatus.tracking_number == tracking_number).first()
    return shipment_status
