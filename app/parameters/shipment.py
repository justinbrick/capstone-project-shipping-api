"""
Shipment query parameters.
"""

__author__ = "Justin B. (justin@justin.directory)"


from typing import Optional
from uuid import UUID

from app.parameters.pagination import PaginationParams
from app.shipping.enums import Provider, Status


class BaseShipmentQueryParams(PaginationParams):
    """
    Common parameters to query for in multiple shipments.
    """
    status: Optional[Status] = None
    """The shipment status to filter by."""
    provider: Optional[Provider] = None
    """The shipment provider to filter by."""
    from_address: Optional[str] = None
    """The address to filter by. This is a wildcard search."""
    shipping_address: Optional[str] = None
    """The shipping address to filter by. This is a wildcard search."""
    delivery_id: Optional[UUID] = None
    """The delivery ID to filter by."""


class FullShipmentQueryParams(BaseShipmentQueryParams):
    """
    Full shipment query parameters, only used in the shipments endpoint.
    """
    user_id: Optional[UUID] = None
    """The user ID to filter by."""
