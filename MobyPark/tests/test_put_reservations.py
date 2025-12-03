# import requests
# import pytest
# from DataAccesLayer.vehicle_access import VehicleAccess
# from DataModels.vehicle_model import VehicleModel

# from DataAccesLayer.db_utils_users import delete

# BASE_URL = "http://localhost:8000"

# def get_session_token(user_data):
#     response = requests.post(f"{BASE_URL}/login", json=user_data)
#     return response.json()

# def test_put_reservations_endpoint():
#     DummyUserOne = {
#         "username": "sezeven",
#         "password": "321",
#         "name": "sezeven Hashemy",
#         "email": "sezeven@gmail.com",
#         "phone": "+31022293944",
#         "birth_year": 2000
#     }

#     DummyVehicleOne = {
#         "license_plate": "34-OOO-3", 
#         "make": "Ford", 
#         "model": "Sport", 
#         "color": "Red", 
#         "year": "2020"
#     }

#     DummyReservationOne = {
#         "parking_lot_id": "1", 
#         "start_time": "2025-12-22 18:00:00",
#         "end_time": "2025-12-22 19:00:00",
#         "status": "confirmed",
#         "created_at": "2025-12-22 18:00:00",
#         "cost": 14,
#     }

#     UpdatedDummyReservationOne = {
#         "parking_lot_id": "2", 
#         "start_time": "2025-12-22 18:00:00",
#         "end_time": "2025-12-22 18:30:00",
#         "status": "confirmed",
#         "created_at": "2025-12-22 18:00:00",
#         "cost": 8,
#         "updated_at": "none"
#     }


#     requests.post(f"{BASE_URL}/register", json=DummyUserOne)

#     user_data = get_session_token(DummyUserOne)
#     user_id = user_data.get("user_id")
#     token1 = user_data.get("session_token")
#     headers1 = {"Authorization": token1}

#     vehicle_result = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers1)
#     vehicle_data = vehicle_result.json()
#     vehicle_model = vehicle_data["vehicle"]
#     vehicle_obj = VehicleModel(**vehicle_model)

#     create_response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers1)
#     reservation_data_one = create_response.json()
#     reservation_id_one = reservation_data_one["reservation"]["id"]

#     response = requests.put(f"{BASE_URL}/reservations/{reservation_id_one}", json=UpdatedDummyReservationOne, headers=headers1)
#     assert response.status_code == 200

#     reservation_data_two = response.json()
#     reservation_id_two = reservation_data_two["reservation"]["id"]


#     requests.delete(f"{BASE_URL}/reservations/{reservation_id_two}",headers=headers1)
#     VehicleAccess.delete(vehicle_obj)
#     delete(user_id)


#     #reservation not found test below

#     requests.post(f"{BASE_URL}/register", json=DummyUserOne)

#     user_data = get_session_token(DummyUserOne)
#     user_id = user_data.get("user_id")
#     token2 = user_data.get("session_token")
#     headers2 = {"Authorization": token2}

#     vehicle_result = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers2)
#     vehicle_data = vehicle_result.json()
#     vehicle_model = vehicle_data["vehicle"]
#     vehicle_obj = VehicleModel(**vehicle_model)

#     response = requests.put(f"{BASE_URL}/reservations/{9999999999999999}", json=UpdatedDummyReservationOne, headers=headers2)
#     assert response.status_code == 404
#     assert response.text == "Reservation not found"


#     VehicleAccess.delete(vehicle_obj)
#     delete(user_id)


#     # Access denied test below

#     requests.post(f"{BASE_URL}/register", json=DummyUserOne)

#     user_data = get_session_token(DummyUserOne)
#     user_id = user_data.get("user_id")
#     token3 = user_data.get("session_token")
#     headers3 = {"Authorization": token3}

#     vehicle_result = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicleOne, headers=headers3)
#     vehicle_data = vehicle_result.json()
#     vehicle_model = vehicle_data["vehicle"]
#     vehicle_obj = VehicleModel(**vehicle_model)

#     create_response = requests.post(f"{BASE_URL}/reservations", json=DummyReservationOne, headers=headers3)
#     reservation_data_three = create_response.json()
#     reservation_id_three = reservation_data_three["reservation"]["id"]

#     response = requests.put(f"{BASE_URL}/reservations/{2000}", json=UpdatedDummyReservationOne, headers=headers3)
#     data = response.json()
#     assert response.status_code == 403
#     assert data["error"] == "Access denied"


#     requests.delete(f"{BASE_URL}/reservations/{reservation_id_three}",headers=headers3)
#     VehicleAccess.delete(vehicle_obj)
#     delete(user_id)
