import requests
import uuid
import random
import string
import pytest
from DataAccesLayer.vehicle_access import VehicleAccess
from DataModels.vehicle_model import VehicleModel
from DataAccesLayer.db_utils_users import delete
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    return response.json()

def create_dummy_user_and_vehicle():
    username = uuid.uuid4().hex[:8]
    random_phonenumber = random.randint(100000000, 999999999)
    random_number_one = random.randint(10, 99)
    random_number_two = random.randint(1, 9)
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))

    dummy_user = {
        "username": username,
        "password": "Password321!",
        "name": "Test User",
        "email": f"{username}@test.com",
        "phone": f"+310{random_phonenumber}",
        "birth_year": 2000
    }

    dummy_vehicle = {
        "license_plate": f"{random_number_one}-{random_letters}-{random_number_two}",
        "make": "Ford",
        "model": "Sport",
        "color": "Red",
        "year": "2020"
    }

    requests.post(f"{BASE_URL}/register", json=dummy_user)
    session_data = get_session_token(dummy_user)

    user_id = session_data["user_id"]
    token = session_data["session_token"]
    headers = {"Authorization": token}

    vehicle_response = requests.post(
        f"{BASE_URL}/vehicles",
        json=dummy_vehicle,
        headers=headers
    )

    vehicle_model = VehicleModel(**vehicle_response.json()["vehicle"])
    return headers, user_id, vehicle_model

def test_start_and_stop_parking_session_happy_path():
    headers, user_id, vehicle_obj = create_dummy_user_and_vehicle()
    payload = {"parking_lot_id": 1, "licenseplate": vehicle_obj.license_plate.upper()}

    start_resp = requests.post(f"{BASE_URL}/parking-lots/sessions/start", json=payload, headers=headers)
    assert start_resp.status_code == 201
    assert start_resp.json()["message"] == "Your session has started"

    stop_resp = requests.post(f"{BASE_URL}/parking-lots/sessions/stop", json=payload, headers=headers)
    assert stop_resp.status_code == 200
    data = stop_resp.json()
    assert data.get("success") == "Parking session stopped"

    VehicleAccess.delete(vehicle_obj)
    delete(user_id)

def test_start_session_duplicate_sad_path():
    headers, user_id, vehicle_obj = create_dummy_user_and_vehicle()
    payload = {"parking_lot_id": 1, "licenseplate": vehicle_obj.license_plate.upper()}

    first = requests.post(f"{BASE_URL}/parking-lots/sessions/start", json=payload, headers=headers)
    assert first.status_code == 201

    second = requests.post(f"{BASE_URL}/parking-lots/sessions/start", json=payload, headers=headers)
    assert second.status_code == 409
    data = second.json()
    assert data["error"] == "This vehicle is already parked"

    requests.post(f"{BASE_URL}/parking-lots/sessions/stop", json=payload, headers=headers)
    VehicleAccess.delete(vehicle_obj)
    delete(user_id)

def test_start_session_unauthorized_sad_path():
    payload = {"parking_lot_id": 1, "licenseplate": "XX-AAA-1"}

    resp = requests.post(f"{BASE_URL}/parking-lots/sessions/start", json=payload)
    assert resp.status_code == 401
    assert "Unauthorized" in resp.text

def test_stop_session_not_found_sad_path():
    headers, user_id, vehicle_obj = create_dummy_user_and_vehicle()
    payload = {"parking_lot_id": 1, "licenseplate": "NON-EXISTING"}

    resp = requests.post(f"{BASE_URL}/parking-lots/sessions/stop", json=payload, headers=headers)
    assert resp.status_code == 404
    assert resp.json()["error"] == "No active session found"

    VehicleAccess.delete(vehicle_obj)
    delete(user_id)
