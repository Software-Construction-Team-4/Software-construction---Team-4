# import requests
# import uuid
# import random
# import string

# from DataAccesLayer.vehicle_access import VehicleAccess
# from DataModels.vehicle_model import VehicleModel
# from DataAccesLayer.db_utils_users import delete

# BASE_URL = "http://localhost:8000"


# def get_session_token(user_data):
#     response = requests.post(f"{BASE_URL}/login", json=user_data)
#     return response.json()


# def create_dummy_user_and_vehicle():
#     username = uuid.uuid4().hex[:8]
#     random_phonenumber = random.randint(100000000, 999999999)
#     random_number_one = random.randint(10, 99)
#     random_number_two = random.randint(1, 9)
#     random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))

#     dummy_user = {
#         "username": username,
#         "password": "Password321!",
#         "name": "Test User",
#         "email": f"{username}@test.com",
#         "phone": f"+310{random_phonenumber}",
#         "birth_year": 2000
#     }

#     dummy_vehicle = {
#         "license_plate": f"{random_number_one}-{random_letters}-{random_number_two}",
#         "make": "Ford",
#         "model": "Sport",
#         "color": "Red",
#         "year": "2020"
#     }

#     requests.post(f"{BASE_URL}/register", json=dummy_user)
#     session_data = get_session_token(dummy_user)

#     user_id = session_data["user_id"]
#     token = session_data["session_token"]
#     headers = {"Authorization": token}

#     vehicle_response = requests.post(
#         f"{BASE_URL}/vehicles",
#         json=dummy_vehicle,
#         headers=headers
#     )

#     vehicle_model = VehicleModel(**vehicle_response.json()["vehicle"])
#     return headers, user_id, vehicle_model


# def test_start_and_stop_parking_session_happy_path():
#     headers, user_id, vehicle_obj = create_dummy_user_and_vehicle()

#     payload = {
#         "parking_lot_id": "1",
#         "licenseplate": vehicle_obj.license_plate
#     }

#     start_response = requests.post(
#         f"{BASE_URL}/parking-lots/sessions/start",
#         json=payload,
#         headers=headers
#     )

#     assert start_response.status_code == 201
#     assert start_response.json()["message"] == "Your session has started"

#     stop_response = requests.post(
#         f"{BASE_URL}/parking-lots/sessions/stop",
#         json=payload,
#         headers=headers
#     )

#     assert stop_response.status_code == 200
#     data = stop_response.json()

#     assert data["parking_lot_id"] == 1
#     assert data["licenseplate"] == vehicle_obj.license_plate
#     assert data["payment_status"] == "unpaid"

#     VehicleAccess.delete(vehicle_obj)
#     delete(user_id)


# def test_start_session_duplicate_sad_path():
#     headers, user_id, vehicle_obj = create_dummy_user_and_vehicle()

#     payload = {
#         "parking_lot_id": "1",
#         "licenseplate": vehicle_obj.license_plate
#     }

#     first = requests.post(
#         f"{BASE_URL}/parking-lots/sessions/start",
#         json=payload,
#         headers=headers
#     )
#     assert first.status_code == 201

#     second = requests.post(
#         f"{BASE_URL}/parking-lots/sessions/start",
#         json=payload,
#         headers=headers
#     )

#     assert second.status_code == 409
#     data = second.json()
#     assert data["error"] == "Active session already exists for this license plate"

#     requests.post(
#         f"{BASE_URL}/parking-lots/sessions/stop",
#         json=payload,
#         headers=headers
#     )

#     VehicleAccess.delete(vehicle_obj)
#     delete(user_id)


# def test_start_session_unauthorized_sad_path():
#     payload = {
#         "parking_lot_id": "1",
#         "licenseplate": "XX-AAA-1"
#     }

#     response = requests.post(
#         f"{BASE_URL}/parking-lots/sessions/start",
#         json=payload
#     )

#     assert response.status_code == 401
#     assert "Unauthorized" in response.text


# def test_stop_session_not_found_sad_path():
#     headers, user_id, vehicle_obj = create_dummy_user_and_vehicle()

#     payload = {
#         "parking_lot_id": "1",
#         "licenseplate": "NON-EXISTING"
#     }

#     response = requests.post(
#         f"{BASE_URL}/parking-lots/sessions/stop",
#         json=payload,
#         headers=headers
#     )

#     assert response.status_code == 404
#     assert response.json()["error"] == "No active session found for this plate in this parking lot"

#     VehicleAccess.delete(vehicle_obj)
#     delete(user_id)
