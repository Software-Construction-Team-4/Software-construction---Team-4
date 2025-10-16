import requests
import pytest

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "c32d49b3-3875-49b1-841e-a89300ec5f0e"

@pytest.mark.parametrize("vehicle", ["vehicle"])
def test_vehicle_endpoints(vehicle):
    headers = {"Authorization": ADMIN_TOKEN}

    data = {
        "license_plate": "AB-123-CD",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blue",
        "year": 2024,
        "name": "MyCar"
    }

    # vehicle aanmaken
    resp = requests.post(f"{BASE_URL}/vehicles", headers=headers, json=data)
    assert resp.status_code in [200, 201]
    vid = resp.text.split(":")[-1].strip()

    # vehicle ophalen
    resp = requests.get(f"{BASE_URL}/vehicles/{vid}", headers=headers)
    assert resp.status_code == 200
    v_data = resp.json()
    assert v_data["license_plate"] == "AB-123-CD"

    # vehicle updaten
    update_data = {
        "license_plate": "XY-987-ZT",
        "make": "Honda",
        "model": "Civic",
        "color": "Red",
        "year": 2025,
        "name": "UpdatedCar"
    }
    resp = requests.put(f"{BASE_URL}/vehicles/{vid}", headers=headers, json=update_data)
    assert resp.status_code == 200

    # data ophalen om te kijken of update is gelukt
    resp = requests.get(f"{BASE_URL}/vehicles/{vid}", headers=headers)
    assert resp.status_code == 200
    v_data = resp.json()
    assert v_data["license_plate"] == "XY-987-ZT"
    assert v_data["year"] == 2025

    # vehicle verwijderen
    resp = requests.delete(f"{BASE_URL}/vehicles/{vid}", headers=headers)
    assert resp.status_code == 200
