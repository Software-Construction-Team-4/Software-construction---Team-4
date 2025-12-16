import unittest
from DataModels.parkingLotsModel import ParkingLot
from DataAccesLayer import db_utils_parkingLots as parkingLot_utils
from decimal import Decimal

class UnitTestParkingLots(unittest.TestCase):
    def test_row_to_parking_lot(self):
        row = {
            "id": 676767,
            "name": "67",
            "location": "67 city",
            "address": "67 street",
            "capacity": 67,
            "active_sessions": 0,
            "reserved": 0,
            "tariff": Decimal("6.7"),
            "daytariff": Decimal("67.0"),
            "created_at": None,
            "latitude": Decimal("6.7"),
            "longitude": Decimal("6.7"),
            "status": "open",
            "closed_reason": None,
            "closed_date": None,
        }

        lot = parkingLot_utils._row_to_parking_lot(row)

        self.assertIsInstance(lot, ParkingLot)
        self.assertEqual(lot.id, 676767)
        self.assertEqual(lot.name, "67")
        self.assertEqual(lot.capacity, 67)
        self.assertEqual(lot.tariff, Decimal("6.7"))
    
    def test_row_to_parking_lot_missingid(self):
        row = {
            "name": "67"
        }

        with self.assertRaises(KeyError):
            parkingLot_utils._row_to_parking_lot(row)

    def test_row_to_parking_lot_capacity(self):
        row = {
            "id": 676767,
            "name": "67",
            "location": "67 city",
            "address": "67 street",
            "capacity": "zeseven"
        }

        lot = parkingLot_utils._row_to_parking_lot(row)

        self.assertEqual(lot.capacity, "zeseven")

if __name__ == "__main__":
    unittest.main()