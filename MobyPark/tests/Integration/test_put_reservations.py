# import pytest
# import requests
# import random

# from DataAccesLayer.vehicle_access import VehicleAccess
# from DataAccesLayer.db_utils_users import delete as delete_user
# from DataModels.vehicle_model import VehicleModel

# import os
# BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


# def build_random_user():
#     return {
#         "username": f"sezeven_{random.randint(1000,9999)}",
#         "password": "Password321!",
#         "name": "sezeven Hashemy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+310{random.randint(100000000, 999999999)}",
#         "birth_year": 2000
#     }


# def get_session_token(user_data):
#     response = requests.post(f"{BASE_URL}/login", json=user_data)
#     if response.status_code != 200:
#         print("LOGIN FAILED", response.text)
#         pytest.fail("Login failed")
#     return response.json()


# def register_and_login(user):
#     register_response = requests.post(f"{BASE_URL}/register", json=user)
#     if register_response.status_code != 201:
#         pytest.fail(f"User registration failed: {register_response.status_code} {register_response.text}")

#     user_data = get_session_token(user)
#     token = user_data.get("session_token")
#     user_id = user_data.get("user_id")
#     headers = {"Authorization": token}
#     return user_id, headers


# @pytest.fixture
# def user_with_cleanup():
#     user = build_random_user()
#     user_id, headers = register_and_login(user)

#     yield {"user": user, "headers": headers, "user_id": user_id}

#     try:
#         vehicles = VehicleAccess.get_all_user_vehicles(user_id)
#         for v in vehicles:
#             VehicleAccess.delete(v)
#         delete_user(user_id)
#     except Exception as e:
#         print(f"[TEST CLEANUP ERROR] {e}")


# def create_vehicle(headers):
#     dummy_vehicle = {
#         "license_plate": f"34-OOO-{random.randint(1,9)}",
#         "make": "Ford",
#         "model": "Sport",
#         "color": "Red",
#         "year": "2020"
#     }

#     vehicle_result = requests.post(f"{BASE_URL}/vehicles", json=dummy_vehicle, headers=headers)
#     assert vehicle_result.status_code == 201, vehicle_result.text

#     vehicle_model = vehicle_result.json()["vehicle"]
#     return VehicleModel(**vehicle_model)


# def create_reservation(headers, vehicle_id, parking_lot_id=1):
#     dummy_reservation = {
#         "parking_lot_id": parking_lot_id,
#         "vehicle_id": vehicle_id,
#         "start_time": "2030-12-22 18:00:00",
#         "end_time": "2030-12-22 19:00:00",
#         "status": "confirmed",
#         "cost": 14,
#     }

#     r = requests.post(f"{BASE_URL}/reservations", json=dummy_reservation, headers=headers)
#     assert r.status_code in (200, 201), r.text
#     return r.json()["reservation"]["id"]


# def test_put_reservations_endpoint(user_with_cleanup):
#     headers = user_with_cleanup["headers"]

#     updated_reservation = {
#         "start_time": "2030-12-22 18:00:00",
#         "end_time": "2030-12-22 18:30:00"
#     }

#     vehicle_obj = create_vehicle(headers)

#     reservation_id_updated = None
#     reservation_id_a = None
#     user_b_id = None

#     try:
#         reservation_id = create_reservation(headers, vehicle_obj.id)  # CHANGED: pass vehicle_id

#         response = requests.put(
#             f"{BASE_URL}/reservations/{reservation_id}",
#             json=updated_reservation,
#             headers=headers
#         )
#         assert response.status_code == 200, response.text

#         reservation_id_updated = response.json()["reservation"]["id"]

#         del_resp = requests.delete(
#             f"{BASE_URL}/reservations/{reservation_id_updated}",
#             headers=headers
#         )
#         assert del_resp.status_code in (200, 204), del_resp.text

#         response_nf = requests.put(
#             f"{BASE_URL}/reservations/{9999999999999999}",
#             json=updated_reservation,
#             headers=headers
#         )
#         assert response_nf.status_code == 404
#         assert response_nf.text == "Reservation not found"

#         reservation_id_a = create_reservation(headers, vehicle_obj.id)  # CHANGED: pass vehicle_id

#         user_b = build_random_user()
#         user_b_id, headers_b = register_and_login(user_b)

#         denied = requests.put(
#             f"{BASE_URL}/reservations/{reservation_id_a}",
#             json=updated_reservation,
#             headers=headers_b
#         )

#         assert denied.status_code in (403, 404), denied.text

#         if denied.status_code == 403:
#             data = denied.json()
#             assert data["error"] == "Access denied"
#         else:
#             assert denied.text == "Reservation not found"

#     finally:
#         if reservation_id_a is not None:
#             try:
#                 requests.delete(f"{BASE_URL}/reservations/{reservation_id_a}", headers=headers)
#             except Exception:
#                 pass

#         if user_b_id is not None:
#             try:
#                 vehicles_b = VehicleAccess.get_all_user_vehicles(user_b_id)
#                 for v in vehicles_b:
#                     VehicleAccess.delete(v)
#                 delete_user(user_b_id)
#             except Exception:
#                 pass

#         try:
#             VehicleAccess.delete(vehicle_obj)
#         except Exception:
#             pass
