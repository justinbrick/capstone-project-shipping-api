"""
Integration tests for the shipments endpoint.
"""


# @pytest.mark.dependency()
# def test_create_shipment():
#     """
#     Test the creation of a shipment, given fake data.
#     """
#     global expected_shipment_id
#     shipping_address = "Pilsbury Doughboy Lane"
#     provider = "ups"
#     items = []
#     response = test_client.post(
#         "/shipments/", json={"shipping_address": shipping_address, "from_address": shipping_address, "provider": provider, "items": items})
#     assert response.status_code == 200
#     json = response.json()
#     assert json["shipping_address"] == shipping_address
#     assert json["provider"] == provider
#     assert json["shipment_id"] is not None
#     expected_shipment_id = json["shipment_id"]


# @pytest.mark.dependency(depends=["test_create_shipment"])
# def test_get_shipment():
#     """
#     Test the retrieval of a shipment using data that has already been put into the database.
#     """
#     response = test_client.get(f"/shipments/{expected_shipment_id}")
#     assert response.status_code == 200
#     assert response.json()["shipment_id"] == expected_shipment_id
