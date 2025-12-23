import unittest
from DataModels.parkingLotsModel import ParkingLot
from DataAccesLayer import db_utils_parkingLots as parkingLot_utils
from decimal import Decimal

class ParkingLotsDictToLot(unittest.TestCase):
    def test_row_to_lot(self):
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
    
    def test_row_to_lot_no_id(self):
        row = {
            "name": "67",
            "location": "67 city",
            "address": "67 street",
            "capacity": 67,
        }

        with self.assertRaises(KeyError):
            parkingLot_utils._row_to_parking_lot(row)

    def test_row_to_lot_no_name(self):
        row = {
            "id": 676767,
            "location": "67 city",
            "address": "67 street",
            "capacity": "67"
        }
        with self.assertRaises(KeyError):
            parkingLot_utils._row_to_parking_lot(row)

    def test_row_to_lot_no_location(self):
        row = {
            "id": 676767,
            "name": "67",
            "address": "67 street",
            "capacity": "67"
        }
        with self.assertRaises(KeyError):
            parkingLot_utils._row_to_parking_lot(row)

    def test_row_to_lot_no_address(self):
        row = {
            "id": 676767,
            "name": "67",
            "location": "67 city",
            "capacity": "67"
        }
        with self.assertRaises(KeyError):
            parkingLot_utils._row_to_parking_lot(row)

    def test_row_to_lot_no_capacity(self):
        row = {
            "id": 676767,
            "name": "67",
            "location": "67 city",
            "address": "67 street",
        }
        with self.assertRaises(KeyError):
            parkingLot_utils._row_to_parking_lot(row)

    def test_row_to_lot_daytariff(self):
        row = {
            "id": 676767,
            "name": "67",
            "location": "67 city",
            "address": "67 street",
            "capacity": 67,
            "daytariff": None
        }
        lot = parkingLot_utils._row_to_parking_lot(row)
        self.assertIsNone(lot.daytariff)

if __name__ == "__main__":
    unittest.main()