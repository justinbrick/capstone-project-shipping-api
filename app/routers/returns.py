"""
A router to create/return a shipment.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import get_db
from ..database import shipments as db_shipments
from ..shipping.models import CreateShipmentRequest, Provider, Shipment

router = APIRouter()

