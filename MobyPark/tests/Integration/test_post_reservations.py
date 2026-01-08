import requests
import pytest
import random
import uuid
import string

from DataAccesLayer.vehicle_access import VehicleAccess
from DataModels.vehicle_model import VehicleModel

from DataAccesLayer.db_utils_users import delete

import os
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    return response.json()

def test_post_reservations_endpoint():
    username = uuid.uuid4().hex[:8]
    random_phonenumber = random.randint(100000000, 999999999)
    random_number_one = random.randint(10, 99)
    random_number_two = random.randint(1, 9)
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))

    DummyUserOne = {
        "username": f"{username}",
        "password": "Password321!",
        "name": "sezeven Hashemy",
        "email": f"sezeven{username}@gmail.com",
        "phone": f"+310{random_phonenumber}",
        "birth_year": 2000
    }

    DummyVehicleOne = {
        "license_plate": f"{random_number_one}-{random_letters}-{random_number_two}", 
        "make": "Ford", 
        "model": "Sport", 
        "color": "Red", 
        "year": "2020"
    }

    DummyReservationOne = {
        "parking_lot_id": "1", 
        "start_time": "2025-12-22 18:00:00",
        "end_time": "2025-12-22 19:00:00",
        "cost": 14,
    }

    requests.post(f"{BASE_URL}/register", json=DummyUserOne)

    user_data = get_session_token(DummyUserOne)
    user_id = user_data.get("user_id")
    token1 = user_data.get("session_token")
    headers1 = {"Authorization": token1}

    response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers1)
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "User is not registered to any vehicle"

    vehicle_result = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers1)
    vehicle_data = vehicle_result.json()
    vehicle_model = vehicle_data["vehicle"]
    vehicle_obj = VehicleModel(**vehicle_model)

    response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers1)
    assert response.status_code == 201

    reservation_data = response.json()
    reservation_id = reservation_data["reservation"]["id"]

    requests.delete(f"{BASE_URL}/reservations/{reservation_id}",headers=headers1)

    VehicleAccess.delete(vehicle_obj)
    delete(user_id)

    DummyUserTwo = {
        "username": f"{username}",
        "password": "Password321!",
        "name": "zevensez Hashemy",
        "email": f"zevensez{username}@gmail.com",
        "phone": f"+310{random_phonenumber}",
        "birth_year": 2000
    }

    DummyVehicleTwo = {
        "license_plate": f"{random_number_one}-{random_letters}-{random_number_two}", 
        "make": "Ford", 
        "model": "Sport", 
        "color": "Red", 
        "year": "2020"
    }

    DummyReservationTwo = {
        "parking_lot_id": "99999999",
        "start_time": "2025-12-22 18:00:00",
        "end_time": "2025-12-22 19:00:00",
        "cost": 14,
    }

    requests.post(f"{BASE_URL}/register", json=DummyUserTwo)

    user_data = get_session_token(DummyUserTwo)
    user_id = user_data.get("user_id")
    token2 = user_data.get("session_token")
    headers2 = {"Authorization": token2}

    vehicle_result = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleTwo, headers=headers2)
    vehicle_data = vehicle_result.json()
    vehicle_model = vehicle_data["vehicle"]
    vehicle_obj = VehicleModel(**vehicle_model)

    response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationTwo, headers=headers2)
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Parking lot not found"

    VehicleAccess.delete(vehicle_obj)
    delete(user_id)