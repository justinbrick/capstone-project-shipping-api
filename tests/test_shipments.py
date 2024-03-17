from typing import Optional
from fastapi.testclient import TestClient # or starlette
from app.main import app
from uuid import uuid4
import pytest

client = TestClient(app=app)
expected_shipment_id : Optional[str] = None

@pytest.mark.dependency() 
def test_create_shipment():
    global expected_shipment_id
    order_id = str(uuid4())
    shipping_address = "Pilsbury Doughboy Lane"
    provider = "UPS"
    response = client.post("/shipments/", json={"order_id": order_id, "shipping_address": shipping_address, "provider": provider})
    assert response.status_code == 200
    json = response.json()
    assert json["order_id"] == order_id
    assert json["shipping_address"] == shipping_address
    assert json["provider"] == provider
    assert json["shipment_id"] != None
    expected_shipment_id = json["shipment_id"]

@pytest.mark.dependency(depends=["test_create_shipment"])
def test_get_shipment():
    response = client.get(f"/shipments/{expected_shipment_id}")
    assert response.status_code == 200
    assert response.json()["shipment_id"] == expected_shipment_id