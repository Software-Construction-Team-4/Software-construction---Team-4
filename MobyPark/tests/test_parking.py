# import requests
# import pytest

# BASE_URL = "http://localhost:8000"
# ADMIN_TOKEN = "a53cdf9c-10cc-429c-a52c-c92b15a87132"

# @pytest.mark.parametrize("parkinglot", ["parking", "sessions"])
# def test_parking_lot_endpoints(parkinglot):
#     headers = {"Authorization": ADMIN_TOKEN}

#     data = {"name": "testlot", "location": "testlocatie", "capacity": 100}

#     # parking lot maken
#     resp = requests.post(f"{BASE_URL}/parking-lots", headers=headers, json=data)
#     assert resp.status_code in [200, 201]
#     lid = resp.text.split(":")[-1].strip()

#     # parking lot ophalen
#     resp = requests.get(f"{BASE_URL}/parking-lots/{lid}", headers=headers)
#     assert resp.status_code == 200
#     pl_data = resp.json()
#     assert pl_data["capacity"] == 100

#     # parking lot updaten
#     update_data = {"name": "Updated Lot", "location": "Uptown", "capacity": 120}
#     resp = requests.put(f"{BASE_URL}/parking-lots/{lid}", headers=headers, json=update_data)
#     assert resp.status_code == 200

#     # data ophalen om te kijken of update is gelukt
#     resp = requests.get(f"{BASE_URL}/parking-lots/{lid}", headers=headers)
#     assert resp.status_code == 200
#     pl_data = resp.json()
#     assert pl_data["capacity"] == 120

#     # parking lot weer verwijderen
#     resp = requests.delete(f"{BASE_URL}/parking-lots/{lid}", headers=headers)
#     assert resp.status_code == 200