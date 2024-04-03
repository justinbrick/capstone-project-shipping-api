"""
Common constants that are used in testing.
"""

from fastapi.testclient import TestClient
from datetime import datetime
import jwt

from app.main import app

# An unsigned test JWT, used for testing purposes.
jwt_content = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": int(datetime.now().timestamp()),
    "scp": "Shipment.Write Shipment.Read Shipment.Create",
    "extension_roles": "Admin Test"
}
test_jwt = jwt.encode(jwt_content, "test")

test_client = TestClient(app=app, headers={"Authorization": f"Bearer {test_jwt}"})
