import unittest
from DataAccesLayer import db_utils_parkingSessions as session_utils
from decimal import Decimal
from unittest.mock import MagicMock, patch

class ParkingSessionsDictToSession(unittest.TestCase):
    def test_row_to_session(self):
        row = {
            "id": 696969,
            "parking_lot_id": 69,
            "session": 1,
            "user": 1,
            "licenseplate": "XYZ-110",
            "started": None,
            "stopped": None,
            "duration_minutes": 0,
            "cost": Decimal("6.9"),
            "payment_status": "PENDING"
        }

        session = session_utils._row_to_parking_session(row)

        self.assertEqual(session.id, 696969)
        self.assertEqual(session.parking_lot_id, 69)
        self.assertEqual(session.user_id, 1)
        self.assertEqual(session.licenseplate, "XYZ-110")
        self.assertEqual(session.payment_status, "PENDING")

    def test_start_session(self):
        with patch("DataAccesLayer.db_utils_parkingSessions.get_db_connection") as db_connection:
            db_cursor = MagicMock()
            db_connection.return_value.cursor.return_value = db_cursor
            db_cursor.fetchone.side_effect = [None, {"next_num": 1}]

            result = session_utils.start_session(69, "XYZ-110", 1)
            self.assertTrue(result.get("ok"))
            self.assertTrue(db_cursor.execute.called)

if __name__ == "__main__":
    unittest.main()
