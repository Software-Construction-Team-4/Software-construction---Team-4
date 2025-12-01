import requests
import pytest

BASE_URL = "http://localhost:8000"

def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    return response.json().get("session_token")

def test_post_reservations_endpoint():
    DummyUserOne = {
        "username": "sezeven",
        "password": "321",
        "name": "sezeven Hashemy",
        "email": "sezeven@gmail.com",
        "phone": "+31022293944",
        "birth_year": 2000
    }

    DummyVehicleOne = {
        "license_plate": "34-OOO-3", 
        "make": "Ford", 
        "model": "Sport", 
        "color": "Red", 
        "year": "2020"
    }

    DummyReservationOne = {
        "parking_lot_id": "1", 
        "start_time": "2025-12-22 18:00:00",
        "end_time": "2025-12-22 19:00:00",
        "status": "confirmed",
        "created_at": "2025-12-22 18:00:00",
        "cost": 14,
    }

    requests.post(f"{BASE_URL}/register", json=DummyUserOne)
    token1 = get_session_token(DummyUserOne)
    headers1 = {"Authorization": token1}

    response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers1)
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "User is not registerd to any vehicle"

    requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers1)
    response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers1)
    assert response.status_code == 201

    reservation_data = response.json()
    reservation_id = reservation_data["reservation"]["id"]
    vehicle_id = reservation_data["reservation"]["vehicle_id"]

    requests.delete(f"{BASE_URL}/reservations/{reservation_id}",headers=headers1)
    requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}",headers=headers1)


    DummyUserTwo = {
        "username": "zevensez",
        "password": "321",
        "name": "zevensez Hashemy",
        "email": "zevensez@gmail.com",
        "phone": "+31022293944",
        "birth_year": 2000
    }

    DummyVehicleTwo = {
        "license_plate": "34-BBB-3", 
        "make": "Ford", 
        "model": "Sport", 
        "color": "Red", 
        "year": "2020"
    }

    DummyReservationTwo = {
        "parking_lot_id": "99999999",
        "start_time": "2025-12-22 18:00:00",
        "end_time": "2025-12-22 19:00:00",
        "status": "confirmed",
        "created_at": "2025-12-22 18:00:00",
        "cost": 14,
    }

    requests.post(f"{BASE_URL}/register", json=DummyUserTwo)
    token2 = get_session_token(DummyUserTwo)
    headers2 = {"Authorization": token2}

    vehicle_response = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleTwo, headers=headers2)

    vehicle_data = vehicle_response.json()
    vehicle_id = vehicle_data["vehicle"]["id"]

    response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationTwo, headers=headers2)
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Parking lot not found"

    requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}",headers=headers2)


