# test_put_vehicle.py

import random
import pytest
import requests

from DataAccesLayer.vehicle_access import VehicleAccess
from DataAccesLayer.db_utils_users import delete as delete_user  # delete user by id

import os
from environment import Environment
BASE_URL = Environment.get_var("BASE_URL", "http://localhost:8000")


def make_random_user(prefix: str):
    """Create a random user dict to avoid collisions in the DB."""
    suffix = random.randint(1000, 9999)
    return {
        "username": f"{prefix}{suffix}",
        "password": "Password321!",
        "name": f"Test User",
        "email": f"{prefix}{suffix}@gmail.com",
        "phone": f"+310{random.randint(100000000, 999999999)}",
        "birth_year": 2000,
    }


def get_session_data(user_data):
    """Login and return the full JSON body, failing loudly on error."""
    response = requests.post(f"{BASE_URL}/login", json=user_data)

    if response.status_code != 200:
        print("LOGIN FAILED", response.status_code, response.text)
        pytest.fail("Login failed")

    return response.json()  # contains session_token and user_id


# --- Create one random user up-front, like in test_vehicles.py ---

random_user = make_random_user("veh_put_one_")

register_response = requests.post(f"{BASE_URL}/register", json=random_user)
if register_response.status_code != 201:
    pytest.fail(
        f"User registration failed: {register_response.status_code} {register_response.text}"
    )

user_data = get_session_data(random_user)
token = user_data.get("session_token")
user_id = user_data.get("user_id")
headers = {"Authorization": token}


@pytest.fixture
def user_with_vehicle_and_cleanup():
    ValidVehicle = {
        "license_plate": "99-XYZ-1",
        "make": "Tesla",
        "model": "Model 3",
        "color": "White",
        "year": "2022",
    }

    # Create initial vehicle for the user
    response = requests.post(
        f"{BASE_URL}/vehicles",
        json=ValidVehicle,
        headers=headers,
    )
    assert response.status_code == 201
    vehicle_data = response.json()
    vehicle_id = vehicle_data["vehicle"]["id"]

    yield {
        "headers": headers,
        "user_id": user_id,
        "vehicle_id": vehicle_id,
    }

    # Cleanup vehicles + user
    try:
        vehicles = VehicleAccess.get_all_user_vehicles(user_id)
        for v in vehicles:
            VehicleAccess.delete(v)

        delete_user(user_id)
    except Exception as e:
        print(f"[TEST CLEANUP ERROR] {e}")


def test_put_vehicles_endpoint(user_with_vehicle_and_cleanup):
    headers1 = user_with_vehicle_and_cleanup["headers"]
    vehicle_id = user_with_vehicle_and_cleanup["vehicle_id"]

    IncompleteUpdate = {
        "license_plate": "11-AAA-1",
        "make": "Tesla",
        "model": "Model S",
        "year": "2023",
    }

    UpdatedVehicle = {
        "license_plate": "11-AAA-1",
        "make": "Tesla",
        "model": "Model S",
        "color": "Black",
        "year": "2023",
    }

    # PUT with missing required field -> 400
    response = requests.put(
        f"{BASE_URL}/vehicles/{vehicle_id}",
        json=IncompleteUpdate,
        headers=headers1,
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Required field missing"
    assert data["field"] == "color"

    # PUT with full update -> 200
    response = requests.put(
        f"{BASE_URL}/vehicles/{vehicle_id}",
        json=UpdatedVehicle,
        headers=headers1,
    )
    assert response.status_code == 200

    updated_data = response.json()
    assert updated_data["status"] == "Updated"
    assert updated_data["vehicle"]["id"] == vehicle_id
    assert updated_data["vehicle"]["license_plate"] == UpdatedVehicle["license_plate"]
    assert updated_data["vehicle"]["make"] == UpdatedVehicle["make"]
    assert updated_data["vehicle"]["model"] == UpdatedVehicle["model"]
    assert updated_data["vehicle"]["color"] == UpdatedVehicle["color"]
    assert str(updated_data["vehicle"]["year"]) == str(UpdatedVehicle["year"])
