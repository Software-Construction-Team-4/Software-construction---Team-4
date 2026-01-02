# test_vehicles.py

import uuid
import pytest
import requests
import random

from DataAccesLayer.vehicle_access import VehicleAccess
from DataAccesLayer.db_utils_users import delete as delete_user  # delete user by id

import os
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


random_user = {
    "username": f"sezeven_{random.randint(1000,9999)}",
    "password": "Sez677!!",
    "name": "sezeven Hashemy",
    "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
    "phone": f"+310{random.randint(100000000, 999999999)}",
    "birth_year": 2000
}

def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)

    if response.status_code != 200:
        print("LOGIN FAILED", response.text)
        pytest.fail("Login failed")

    return response.json()

register_response = requests.post(f"{BASE_URL}/register", json=random_user)

if register_response.status_code != 201:
    pytest.fail("User registration failed")

user_data = get_session_token(random_user)
token = user_data.get("session_token")
user_id = user_data.get("user_id")
headers = {"Authorization": token}


@pytest.fixture
def dummy_user_with_cleanup():


    yield {
        "user": random_user,
        "headers": headers,
        "user_id": user_id,
    }


    try:
        vehicles = VehicleAccess.get_all_user_vehicles(user_id)
        for v in vehicles:
            VehicleAccess.delete(v)

        delete_user(user_id)

    except Exception as e:
        print(f"[TEST CLEANUP ERROR] {e}")


def test_post_vehicles_endpoint(dummy_user_with_cleanup):
    headers1 = dummy_user_with_cleanup["headers"]

    IncompleteVehicle = {
        "license_plate": "99-XYZ-1",
        "make": "Tesla",
        "model": "Model 3",
        "year": "2022",
    }

    ValidVehicle = {
        "license_plate": "99-XYZ-1",
        "make": "Tesla",
        "model": "Model 3",
        "color": "White",
        "year": "2022",
    }

    response = requests.post(
        f"{BASE_URL}/vehicles",
        json=IncompleteVehicle,
        headers=headers1
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Missing required fields"
    assert "color" in data["fields"]

    response = requests.post(
        f"{BASE_URL}/vehicles",
        json=ValidVehicle,
        headers=headers1
    )
    assert response.status_code == 201

    vehicle_data = response.json()
    assert vehicle_data["status"] == "Success"
    assert vehicle_data["vehicle"]["license_plate"] == ValidVehicle["license_plate"]
    assert vehicle_data["vehicle"]["make"] == ValidVehicle["make"]
    assert vehicle_data["vehicle"]["model"] == ValidVehicle["model"]
    assert vehicle_data["vehicle"]["color"] == ValidVehicle["color"]
    assert str(vehicle_data["vehicle"]["year"]) == str(ValidVehicle["year"])

    vehicle_id = vehicle_data["vehicle"]["id"]
    assert vehicle_id is not None

    response = requests.post(
        f"{BASE_URL}/vehicles",
        json=ValidVehicle,
        headers=headers1
    )
    assert response.status_code == 409
    data = response.json()
    assert data["error"] == "User already has a vehicle"
