import requests
import pytest

BASE_URL = "http://localhost:8000"

def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    return response.json().get("session_token")

def test_delete_reservations_endpoint():
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

    requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers1)

    creation_result = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers1)
    reservation_data = creation_result.json()
    reservation_id = reservation_data["reservation"]["id"]
    vehicle_id = reservation_data["reservation"]["vehicle_id"]

    get_result = requests.delete(f"{BASE_URL}/reservations/{reservation_id}", json=DummyReservationOne, headers=headers1)
    assert get_result.status_code == 200
    data = get_result.json()
    assert data["status"] == "Deleted"


    requests.delete(f"{BASE_URL}/reservations/{reservation_id}",headers=headers1)
    requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}",headers=headers1)


    # giving wrong reservation id test below

    token2 = get_session_token(DummyUserOne)
    headers2 = {"Authorization": token2}

    requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers2)

    creation_result = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers2)
    reservation_data = creation_result.json()
    reservation_id = reservation_data["reservation"]["id"]
    vehicle_id = reservation_data["reservation"]["vehicle_id"]

    get_result = requests.delete(f"{BASE_URL}/reservations/{reservation_id - 1}", json=DummyReservationOne, headers=headers2)
    assert get_result.status_code == 403
    data = get_result.json()
    assert data["error"] == "Access denied"

    requests.delete(f"{BASE_URL}/reservations/{reservation_id}",headers=headers2)
    requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}",headers=headers2)


