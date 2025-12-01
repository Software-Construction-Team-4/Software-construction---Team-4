import requests
import pytest

BASE_URL = "http://localhost:8000"

def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    return response.json().get("session_token")

def test_put_reservations_endpoint():
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

    UpdatedDummyReservationOne = {
        "parking_lot_id": "2", 
        "start_time": "2025-12-22 18:00:00",
        "end_time": "2025-12-22 18:30:00",
        "status": "confirmed",
        "created_at": "2025-12-22 18:00:00",
        "cost": 8,
        "updated_at": "none"
    }


    requests.post(f"{BASE_URL}/register", json=DummyUserOne)
    token1 = get_session_token(DummyUserOne)
    headers1 = {"Authorization": token1}

    requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers1)
    create_response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers1)
    reservation_data_one = create_response.json()
    reservation_id_one = reservation_data_one["reservation"]["id"]

    response = requests.put(f"{BASE_URL}/reservations/{reservation_id_one}", json=UpdatedDummyReservationOne, headers=headers1)
    assert response.status_code == 200

    reservation_data_two = response.json()
    reservation_id_two = reservation_data_two["reservation"]["id"]
    vehicle_id = reservation_data_two["reservation"]["vehicle_id"]


    requests.delete(f"{BASE_URL}/reservations/{reservation_id_two}",headers=headers1)
    requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}",headers=headers1)


    #reservation not found test below

    token2 = get_session_token(DummyUserOne)
    headers2 = {"Authorization": token2}

    vehicle_response = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers2)
    
    vehicle_data = vehicle_response.json()
    vehicle_id = vehicle_data["vehicle"]["id"]

    response = requests.put(f"{BASE_URL}/reservations/{9999999999999999}", json=UpdatedDummyReservationOne, headers=headers2)
    assert response.status_code == 404
    assert response.text == "Reservation not found"


    requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}",headers=headers2)


    # Access denied test below

    token3 = get_session_token(DummyUserOne)
    headers3 = {"Authorization": token3}

    vehicle_response = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers3)
    
    vehicle_data = vehicle_response.json()
    vehicle_id = vehicle_data["vehicle"]["id"]

    create_response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers3)
    reservation_data_three = create_response.json()
    reservation_id_three = reservation_data_three["reservation"]["id"]

    response = requests.put(f"{BASE_URL}/reservations/{2000}", json=UpdatedDummyReservationOne, headers=headers3)
    data = response.json()
    assert response.status_code == 403
    assert data["error"] == "Access denied"


    requests.delete(f"{BASE_URL}/reservations/{reservation_id_three}",headers=headers3)
    requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}",headers=headers3)

