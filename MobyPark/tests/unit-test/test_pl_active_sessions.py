import unittest
from unittest.mock import MagicMock, patch
from DataAccesLayer import db_utils_parkingLots as parkingLot_utils

class UnitTestParkingLotsActiveSessions(unittest.TestCase):

    def test_active_sessions(self):
        with patch("DataAccesLayer.db_utils_parkingLots.get_db_connection") as db_connection:
            db_cursor = MagicMock()
            db_connection.return_value.cursor.return_value = db_cursor

            parkingLot_utils.increment_active_sessions(67, 1)
            self.assertTrue(db_cursor.execute.called)

            db_cursor.reset_mock()

            parkingLot_utils.increment_active_sessions(67, -2)
            self.assertTrue(db_cursor.execute.called)

if __name__ == "__main__":
    unittest.main()