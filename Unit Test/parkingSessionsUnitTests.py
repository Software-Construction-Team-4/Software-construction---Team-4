import unittest
import requests
import json

BASE_URL = "http://localhost:8000"

AUTH_TOKEN = "ec649f31-7daf-4a22-b180-286a160bf8ce"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": AUTH_TOKEN
}

class TestParkingSessionsAPI(unittest.TestCase):

    def test_start_session(self):
        data = {
            "parking_lot_id": 1,
            "licenseplate": "UNITTESTSTART67"
        }
        r = requests.post(
            f"{BASE_URL}/parking-lots/sessions/start",
            data=json.dumps(data),
            headers=HEADERS
        )
        self.assertEqual(r.status_code, 201)
        res = r.json()
        self.assertIn("session_id", res)

    def test_stop_session(self):
        data = {
            "parking_lot_id": 1,
            "licenseplate": "UNITTESTSTOP67"
        }
        start = requests.post(
            f"{BASE_URL}/parking-lots/sessions/start",
            data=json.dumps(data),
            headers=HEADERS
        )
        self.assertEqual(start.status_code, 201)
        session_id = start.json()["session_id"]

        stop_data = {
            "parking_lot_id": data["parking_lot_id"],
            "licenseplate": data["licenseplate"]
        }
        stop = requests.post(
            f"{BASE_URL}/parking-lots/sessions/stop",
            data=json.dumps(stop_data),
            headers=HEADERS
        )
        self.assertEqual(stop.status_code, 200)
        res = stop.json()
        self.assertEqual(res["licenseplate"], data["licenseplate"])
        self.assertEqual(res["parking_lot_id"], data["parking_lot_id"])

    def test_get_sessions(self):
        r = requests.get(
            f"{BASE_URL}/parking-lots/sessions",
            headers=HEADERS
        )
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), dict)

if __name__ == "__main__":
    unittest.main()
