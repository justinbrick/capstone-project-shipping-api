"""
A router to get user related shipping information.
"""

from fastapi import APIRouter
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import get_db
from app.auth.dependencies import get_profile
from app.auth.profile import AccountProfile
from app.shipping.models import Shipment, ShipmentStatus
from app.shipping.delivery import shipping_providers as shipping_providers
from app.database import schemas

router = APIRouter()


@router.get("/users/{user_id}/shipments", tags=["users"])
def get_user_shipments(user_id: int):
    """
    Logic to query user shipments from the database
    Return the queried shipments as a response
    """

    return {"user_id": user_id, "shipments": []}


def sort_all_shipments(shipments):
    """
    Sort the shipments by the created_at field in descending order
    """

    return sorted(shipments, key=lambda x: x["created_at"], reverse=True)


def sort_undelivered_shipments(shipments):
    """
    Filter out the shipments that have been delivered and sort the remaining shipments by created_at field in descending order
    """

    return sort_all_shipments([shipment for shipment in shipments if shipment["status"] != "delivered"])
