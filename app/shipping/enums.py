"""
Enums for shipping module
"""

from enum import Enum


class Provider(Enum):
    """
    Represents the different providers that can be used to ship a package.
    """
    UPS = "ups"
    FEDEX = "fedex"
    USPS = "usps"
    INTERNAL = "internal"


class Status(Enum):
    """
    The shipment status enum represents the different statuses that a shipment can be in.
    """
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


class SLA(Enum):
    """
    The service level agreement enum represents the different service level agreements that a shipment can be under.
    """
    STANDARD = "standard"  # 3-5 days
    EXPRESS = "express"  # 1-2 days
    OVERNIGHT = "overnight"  # 1 day
    SAME_DAY = "same_day"  # Same day
