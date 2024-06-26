"""
All the routes to get shipping information related to billing orders.
"""

__author__ = "Justin B. (justin@justin.directory)"

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.inventory.warehouse import add_warehouse_stock, remove_warehouse_stock
from app.routers.deliveries import (get_delivery_shipments,
                                    make_delivery_breakdown)
from app.shipping.enums import Provider, Status
from app.shipping.shipment import create_shipment

from ..database import schemas
from ..shipping.models import (CreateDeliveryRequest, CreateReturnRequest,
                               CreateShipmentRequest, Delivery,
                               DeliveryTimeResponse, Return, Shipment)
from ..shipping.providers.internal import client as internal_shipping

router = APIRouter()


@router.get("/{order_id}/deliveries", operation_id="get_order_deliveries")
async def get_order_deliveries(order_id: UUID, db: Session = Depends(get_db)) -> list[Delivery]:
    """
    Get all the deliveries for a given order.

    :param order_id: the ID of the order to get the deliveries for
    """
    deliveries = db.query(schemas.Delivery)\
        .where(schemas.Delivery.order_id == order_id)\
        .all()

    delivery_models: list[Delivery] = []
    for db_delivery in deliveries:
        delivery_shipments = await get_delivery_shipments(db_delivery.delivery_id, db)

        delivery_models.append(Delivery(
            delivery_id=db_delivery.delivery_id,
            order_id=db_delivery.order_id,
            created_at=db_delivery.created_at,
            fulfilled_at=db_delivery.fulfilled_at,
            delivery_sla=db_delivery.delivery_sla,
            shipments=delivery_shipments
        ))
    return delivery_models


@router.post("/{order_id}/deliveries", status_code=201, operation_id="create_order_delivery")
async def create_order_delivery(order_id: UUID, request: CreateDeliveryRequest, db: Session = Depends(get_db)) -> Delivery:
    """
    Create a delivery for a given order.

    :param order_id: the ID of the order to create a delivery for
    :param request: the request to create the delivery
    """
    # We first need to get the delivery breakdown to see if we can meet the SLA.
    delivery_breakdown = await make_delivery_breakdown(request)

    # If we cannot meet the SLA, we should return an error.
    if not delivery_breakdown.can_meet_sla:
        raise HTTPException(
            status_code=400,
            detail={"error": "Cannot meet SLA",
                    "breakdown": delivery_breakdown}
        )

    delivery_id = uuid4()
    shipments: list[Shipment] = []
    db_shipments: list[schemas.Shipment] = []
    successful_item_removals: list[DeliveryTimeResponse] = []
    try:
        for delivery_time in delivery_breakdown.delivery_times:

            # first, remove the stock from the associated warehouse.
            # if this excepts, we should rollback the previous stock removals.
            await remove_warehouse_stock(delivery_time.warehouse_id, delivery_time.items)
            successful_item_removals.append(delivery_time)

            shipment_request = CreateShipmentRequest(
                order_id=order_id,
                shipping_address=request.recipient_address,
                from_address=delivery_time.from_address,
                items=delivery_time.items,
                provider=delivery_time.provider
            )

            # Create the shipment and add it to the list of shipment for the model.
            shipment = await create_shipment(shipment_request)
            shipments.append(shipment)

            # Create the shipment model and add it to the list of delivery infos.
            db_shipment = schemas.Shipment(
                **shipment.model_dump(exclude=["items"]),
                status=schemas.ShipmentStatus(
                    message=Status.PENDING,
                    expected_at=delivery_time.delivery_time,
                    updated_at=datetime.now(),
                    delivered_at=None
                ),
                items=[
                    schemas.ShipmentItem(
                        **item.model_dump()
                    )
                    for item in shipment.items
                ]
            )

            db_shipments.append(db_shipment)

        dump = request.model_dump(exclude=["items"])
        created_at = datetime.now()
        db_delivery = schemas.Delivery(
            delivery_id=delivery_id,
            order_id=order_id,
            created_at=created_at,
            **dump,
            shipments=db_shipments
        )

        db.add(db_delivery)
        db.commit()

        return Delivery(
            delivery_id=delivery_id,
            order_id=order_id,
            created_at=created_at,
            shipments=shipments,

            **dump,
        )
    except Exception as e:
        # If we have an exception, we should rollback the stock removals.
        for delivery_time in successful_item_removals:
            await add_warehouse_stock(delivery_time.warehouse_id, delivery_time.items)

        db.rollback()
        raise e


@router.get("/{order_id}/returns", operation_id="get_order_returns")
async def get_order_returns(order_id: UUID, db: Session = Depends(get_db)) -> list[Return]:
    """
    Get all the returns for a given order.
    """
    returns = db.query(schemas.Return)\
        .where(schemas.Return.order_id == order_id)\
        .all()

    return returns


@router.post("/{order_id}/returns", status_code=201)
async def create_order_return(order_id: UUID, return_request: CreateReturnRequest, db: Session = Depends(get_db)) -> Return:
    """
    Create a return for a given order.
    """
    return_id = uuid4()

    # Create a shipment request, and send to internal_shipping
    # The shipping address will be the Tech Support address.
    shipment_request = CreateShipmentRequest(
        order_id=order_id,
        shipping_address="119 Ranch Dr, Maggie Valley, NC 28751",
        from_address=return_request.from_address,
        items=return_request.items,
        provider=Provider.INTERNAL
    )

    shipment = await internal_shipping.create_shipment(shipment_request)

    db_return = schemas.Return(
        created_at=datetime.now(),
        order_id=order_id,
        return_id=return_id,
        shipment=schemas.Shipment(
            **shipment.model_dump(exclude=["items"]),
            items=[
                schemas.ShipmentItem(**item.model_dump())
                for item in shipment.items
            ]
        )
    )

    db.add(db_return)
    db.commit()

    model_return = Return(
        order_id=order_id,
        return_id=return_id,
        shipment=shipment,
        created_at=db_return.created_at,
        items=return_request.items
    )

    return model_return
