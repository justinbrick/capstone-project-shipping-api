"""
All the routes to get shipping information related to billing orders.
"""

from datetime import datetime
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.routers.deliveries import get_delivery_shipments
from app.shipping.delivery import get_delivery_breakdown
from app.shipping.enums import Provider
from app.shipping.shipment import create_shipment

from ..database import schemas
from app import get_db
from ..shipping.models import CreateDeliveryRequest, CreateReturnRequest, CreateShipmentRequest, Delivery, Return
from ..shipping.providers.internal import client as internal_shipping

router = APIRouter()


@router.get("/{order_id}/deliveries")
async def get_order_deliveries(order_id: UUID, db: Session = Depends(get_db)) -> list[Delivery]:
    """
    Get all the deliveries for a given order.
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


@router.post("/{order_id}/deliveries", status_code=201)
async def create_order_delivery(order_id: UUID, request: CreateDeliveryRequest, db: Session = Depends(get_db)) -> Delivery:
    """
    Create a delivery for a given order.
    """
    delivery_id = uuid4()
    # We first need to get the delivery breakdown to see if we can meet the SLA.
    delivery_breakdown = await get_delivery_breakdown(
        request.recipient_address,
        request.delivery_sla,
        request.items
    )

    # If we cannot meet the SLA, we should return an error.
    if not delivery_breakdown.can_meet_sla:
        raise HTTPException(
            status_code=400,
            detail={"error": "Cannot meet SLA",
                    "breakdown": delivery_breakdown}
        )

    for delivery_time in delivery_breakdown.delivery_times:
        shipment_request = CreateShipmentRequest(
            order_id=order_id,
            shipping_address=request.recipient_address,
            from_address=delivery_time.from_address,
            items=delivery_time.items,
            provider=delivery_time.provider
        )

        shipment = await create_shipment(shipment_request)

        db_shipment = schemas.Shipment(
            **shipment.model_dump(exclude=["items"])
        )

        db_shipment_items = [
            schemas.ShipmentItem(
                shipment_id=shipment.shipment_id,
                upc=item.upc,
                stock=item.stock)
            for item in shipment.items]

        db.add(db_shipment)
        db.add_all(db_shipment_items)
        db.commit()

    dump = request.model_dump(exclude=["items"])
    created_at = datetime.now()
    db_delivery = schemas.Delivery(
        delivery_id=delivery_id,
        order_id=order_id,
        created_at=created_at,
        **dump
    )

    db.add(db_delivery)
    db.commit()

    return db_delivery


@router.get("/{order_id}/returns")
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

    db_shipment = schemas.Shipment(
        shipment_id=shipment.shipment_id,
        from_address=shipment.from_address,
        shipping_address=shipment.shipping_address,
        provider=shipment.provider,
        created_at=shipment.created_at,
        expected_at=shipment.expected_at,
    )

    db.add(db_shipment)
    db.commit()

    db_shipment_items = [
        schemas.ShipmentItem(
            shipment_id=shipment.shipment_id,
            upc=item.upc,
            stock=item.stock)
        for item in shipment.items]

    db.add_all(db_shipment_items)
    db.commit()

    db_return = schemas.Return(
        order_id=order_id,
        return_id=return_id,
        shipment_id=shipment.shipment_id
    )

    db.add(db_return)
    db.commit()

    model_return = Return(
        order_id=order_id,
        return_id=return_id,
        shipment=shipment
    )

    return model_return
