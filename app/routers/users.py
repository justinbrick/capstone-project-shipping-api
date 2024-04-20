"""
A router to get user related shipping information.
"""


from fastapi import APIRouter, HTTPException
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import get_db
from app.parameters.shipment import BaseShipmentQueryParams, FullShipmentQueryParams
from app.routers.shipments import get_shipments
from app.shipping.models import Delivery, Shipment, ShipmentStatus
from app.shipping.delivery import shipping_providers as shipping_providers
from app.database import schemas

router = APIRouter()
"""
Fix router to use correct queries in order to find shipments.
"""


@router.get("/{user_id}/shipments", operation_id="get_user_shipments")
async def get_user_shipments(user_id: UUID, params: BaseShipmentQueryParams = Depends(), db: Session = Depends(get_db)) -> list[Shipment]:
    """
    Get all the shipments for a given user.
    """

    params = FullShipmentQueryParams(
        limit=params.limit,
        offset=params.offset,
        user_id=user_id,
        status=params.status,
        provider=params.provider,
        from_address=params.from_address,
        shipping_address=params.shipping_address,
        delivery_id=params.delivery_id
    )

    return await get_shipments(params, db)


@router.get("/{user_id}/shipments/{shipment_id}", operation_id="get_user_shipment")
async def get_user_shipment(user_id: UUID, shipment_id: UUID, db: Session = Depends(get_db)) -> Shipment:
    """
    Get a specific shipment for a given user.
    """

    shipment = db.query(schemas.Shipment)\
        .join(schemas.ShipmentDeliveryInfo, schemas.Shipment.shipment_id == schemas.ShipmentDeliveryInfo.shipment_id)\
        .join(schemas.Delivery, schemas.ShipmentDeliveryInfo.delivery_id == schemas.Delivery.delivery_id)\
        .join(schemas.Order, schemas.Delivery.order_id == schemas.Order.order_id)\
        .where(schemas.Order.customer_id == user_id)\
        .where(schemas.Shipment.shipment_id == shipment_id)\
        .first()

    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return shipment


@router.get("/{user_id}/shipments/{shipment_id}/status", operation_id="get_user_shipment_status")
async def get_user_shipment_status(user_id: UUID, shipment_id: UUID, db: Session = Depends(get_db)) -> ShipmentStatus:
    """
    Get the status of a shipment for the currently logged in user.
    """

    shipment = await get_user_shipment(user_id, shipment_id, db)
    provider = shipping_providers[shipment.provider]
    return await provider.get_shipment_status(shipment.provider_shipment_id)


@router.get("/{user_id}/deliveries", operation_id="get_user_deliveries")
async def get_user_deliveries(user_id: UUID, db: Session = Depends(get_db)) -> list[Delivery]:
    """
    Get all the deliveries for a given user.
    """

    return db.query(schemas.Delivery)\
        .join(schemas.Order, schemas.Delivery.order_id == schemas.Order.order_id)\
        .where(schemas.Order.customer_id == user_id)\
        .all()
