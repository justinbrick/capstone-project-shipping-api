"""
Common constants that are used in testing.
"""

from datetime import datetime

import jwt
from fastapi.testclient import TestClient

from app.database.dependencies import get_db
from app.main import app

# An unsigned test JWT, used for testing purposes.
jwt_content = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": int(datetime.now().timestamp()),
    "scp": "Shipment.Write Shipment.Read Shipment.Create",
    "extension_roles": "Admin,Test",
    "extension_uflag": True
}
test_jwt = jwt.encode(jwt_content, "test")

test_client = TestClient(
    app=app, headers={"Authorization": f"Bearer {test_jwt}"})
