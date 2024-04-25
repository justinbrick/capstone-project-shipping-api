import unittest
from datetime import datetime
from unittest.mock import MagicMock

from app.shipping.providers import ShipmentStatus, Status, get_current_delivery_progress_estimate


class ShipmentStatusTest(unittest.TestCase):

    def test_get_shipment_status_delivered(self):
        shipment_id = "12345"
        shipment = MagicMock()
        shipment.shipment_id = shipment_id
        shipment.status.expected_at = datetime.now()
        get_current_delivery_progress_estimate.return_value = 1.0

        status = ShipmentStatus().get_shipment_status(shipment_id)

        self.assertEqual(status.shipment_id, shipment_id)
        self.assertEqual(status.expected_at, shipment.status.expected_at)
        self.assertEqual(status.updated_at.date(), datetime.now().date())
        self.assertEqual(status.message, Status.DELIVERED)

    def test_get_shipment_status_pending(self):

        shipment_id = "12345"
        shipment = MagicMock()
        shipment.shipment_id = shipment_id
        shipment.status.expected_at = datetime.now()
        get_current_delivery_progress_estimate.return_value = 0.0

        status = ShipmentStatus().get_shipment_status(shipment_id)

        self.assertEqual(status.shipment_id, shipment_id)
        self.assertEqual(status.expected_at, shipment.status.expected_at)
        self.assertEqual(status.updated_at.date(), datetime.now().date())
        self.assertEqual(status.message, Status.PENDING)

    def test_get_shipment_status_in_transit(self):

        shipment_id = "12345"
        shipment = MagicMock()
        shipment.shipment_id = shipment_id
        shipment.status.expected_at = datetime.now()
        get_current_delivery_progress_estimate.return_value = 0.5

        status = ShipmentStatus().get_shipment_status(shipment_id)

        self.assertEqual(status.shipment_id, shipment_id)
        self.assertEqual(status.expected_at, shipment.status.expected_at)
        self.assertEqual(status.updated_at.date(), datetime.now().date())
        self.assertEqual(status.message, Status.IN_TRANSIT)


if __name__ == '__main__':
    unittest.main()
