import unittest
import requests
import json

BASE_URL = "http://localhost:8000"

class TestParkingLotsAPI(unittest.TestCase):

    def test_get_all_parking_lots(self):
        r = requests.get(f"{BASE_URL}/parking-lots")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), dict)

    def test_create_parking_lot(self):
        data = {
            "name": "UnitTestParkingLot",
            "location": "TestTown",
            "address": "TestStreet",
            "capacity": 567,
            "reserved": 0,
            "tariff": 3,
            "daytariff": 10,
            "latitude": 56.7,
            "longitude": 6.7,
            "status": "open"
        }
        r = requests.post(f"{BASE_URL}/parking-lots", data=json.dumps(data), headers={"Content-Type": "application/json"})
        self.assertEqual(r.status_code, 201)
        res = r.json()
        self.assertIn("id", res)
        self.created_id = res["id"]

    def test_get_parking_lot_by_id(self):
        data = {
            "name": "UnitTestParkingLot",
            "location": "TestTown",
            "address": "TestStreet",
            "capacity": 567
        }
        r = requests.post(f"{BASE_URL}/parking-lots", data=json.dumps(data), headers={"Content-Type": "application/json"})
        lot_id = r.json()["id"]
        get_r = requests.get(f"{BASE_URL}/parking-lots/{lot_id}")
        self.assertEqual(get_r.status_code, 200)
        self.assertEqual(get_r.json()["name"], "UnitTestParkingLot")

    def test_update_parking_lot(self):
        data = {
            "name": "UnitTestParkingLot",
            "location": "TestTown",
            "address": "TestStreet",
            "capacity": 567
        }
        r = requests.post(f"{BASE_URL}/parking-lots", data=json.dumps(data), headers={"Content-Type": "application/json"})
        lot_id = r.json()["id"]
        new_data = {
            "name": "UpdatedUnitTestLot",
            "capacity": 999
        }
        u = requests.put(f"{BASE_URL}/parking-lots/{lot_id}", data=json.dumps(new_data), headers={"Content-Type": "application/json"})
        self.assertEqual(u.status_code, 200)
        check = requests.get(f"{BASE_URL}/parking-lots/{lot_id}").json()
        self.assertEqual(check["name"], "UpdatedUnitTestLot")
        self.assertEqual(check["capacity"], 999)

    def test_delete_parking_lot(self):
        data = {
            "name": "UnitTestParkingLot",
            "location": "TestTown",
            "address": "TestStreet",
            "capacity": 567
        }
        r = requests.post(f"{BASE_URL}/parking-lots", data=json.dumps(data), headers={"Content-Type": "application/json"})
        lot_id = r.json()["id"]
        d = requests.delete(f"{BASE_URL}/parking-lots/{lot_id}")
        self.assertEqual(d.status_code, 200)
        check = requests.get(f"{BASE_URL}/parking-lots/{lot_id}")
        self.assertEqual(check.status_code, 404)

if __name__ == "__main__":
    unittest.main()
