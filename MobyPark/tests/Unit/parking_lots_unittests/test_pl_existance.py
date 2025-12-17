import unittest
from unittest.mock import MagicMock, patch
from DataAccesLayer import db_utils_parkingLots as parkingLot_utils


class ParkingLotsAreReal(unittest.TestCase):

    def test_lot_exists(self):
        with patch("DataAccesLayer.db_utils_parkingLots.get_db_connection") as db_connection:
            db_cursor = MagicMock()
            db_cursor.fetchone.return_value = (1,)
            db_connection.return_value.cursor.return_value = db_cursor

            result = parkingLot_utils.parking_lot_exists(67)

            self.assertTrue(result)

    def test_lot_not_exists(self):
        with patch("DataAccesLayer.db_utils_parkingLots.get_db_connection") as db_connection:
            db_cursor = MagicMock()
            db_cursor.fetchone.return_value = None
            db_connection.return_value.cursor.return_value = db_cursor

            result = parkingLot_utils.parking_lot_exists(676767)

            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
