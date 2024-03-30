"""
Mock FedEx tracking API
"""
from .. import get_db
from ..database import shipments as db_shipments
from ..shipping.models import CreateShipmentRequest, Provider, Shipment
from uuid import UUID, uuid4
"""
TODO: Implement the following functions to complete the FedEx mock API.

1. Mock Database to hold mock tracking numbers and hard coded statuses

2. Add a tracking number to the database when a tracking number is generated

3. Implement get_status and get_location functions to return the status and location of a package with a given tracking number

"""


def generate_tracking_number() -> int:
    """
    Generate a random tracking number.

    :return: the generated tracking number
    """
    generateTrackingNumber = uuid4()
    return generateTrackingNumber


def get_package_location(tracking_number: int) -> str:
    """
    Get the location of a package with a given tracking number.

    :param tracking_number: the tracking number to get the location for
    :return: the location of the package
    """
    return f"Package {tracking_number} is in North Carolina."


def get_package_status(tracking_number: int) -> str:
    """
    Get the status of a package with a given tracking number.

    :param tracking_number: the tracking number to get the status for
    :return: the status of the package
    """
