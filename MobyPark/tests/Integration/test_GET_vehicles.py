# # test_get_vehicles.py

# import random
# import pytest
# import requests

# from DataAccesLayer.vehicle_access import VehicleAccess
# from DataAccesLayer.db_utils_users import delete as delete_user

# BASE_URL = "http://localhost:8000"


# def make_random_user(prefix: str):
#     """Create a random user dict to avoid collisions in the DB."""
#     suffix = random.randint(1000, 9999)
#     return {
#         "username": f"{prefix}{suffix}",
#         "password": "321",
#         "name": f"{prefix} User",
#         "email": f"{prefix}{suffix}@gmail.com",
#         "phone": f"+99{random.randint(10_000_000, 99_999_999)}",
#         "birth_year": 2000,
#     }


# def get_session_data(user_data):
#     """Login and return the full JSON body, failing loudly on error."""
#     response = requests.post(f"{BASE_URL}/login", json=user_data)

#     if response.status_code != 200:
#         print("LOGIN FAILED", response.status_code, response.text)
#         pytest.fail("Login failed")

#     return response.json()


# random_user_one = make_random_user("veh_get_one_")
# random_user_two = make_random_user("veh_get_two_")

# register_response_1 = requests.post(f"{BASE_URL}/register", json=random_user_one)
# if register_response_1.status_code != 201:
#     pytest.fail(f"User1 registration failed: {register_response_1.status_code} {register_response_1.text}")

# user1_data = get_session_data(random_user_one)
# token1 = user1_data.get("session_token")
# user1_id = user1_data.get("user_id")
# headers1 = {"Authorization": token1}

# register_response_2 = requests.post(f"{BASE_URL}/register", json=random_user_two)
# if register_response_2.status_code != 201:
#     pytest.fail(f"User2 registration failed: {register_response_2.status_code} {register_response_2.text}")

# user2_data = get_session_data(random_user_two)
# token2 = user2_data.get("session_token")
# user2_id = user2_data.get("user_id")
# headers2 = {"Authorization": token2}


# @pytest.fixture
# def two_users_with_cleanup():

#     yield {
#         "user1": random_user_one,
#         "user2": random_user_two,
#         "headers1": headers1,
#         "headers2": headers2,
#         "user1_id": user1_id,
#         "user2_id": user2_id,
#     }

#     try:
#         vehicles1 = VehicleAccess.get_all_user_vehicles(user1_id)
#         for v in vehicles1:
#             VehicleAccess.delete(v)

#         vehicles2 = VehicleAccess.get_all_user_vehicles(user2_id)
#         for v in vehicles2:
#             VehicleAccess.delete(v)

#         delete_user(user1_id)
#         delete_user(user2_id)

#     except Exception as e:
#         print(f"[TEST CLEANUP ERROR] {e}")


# def test_get_vehicles_endpoint(two_users_with_cleanup):
#     headers1 = two_users_with_cleanup["headers1"]
#     headers2 = two_users_with_cleanup["headers2"]

#     ValidVehicle = {
#         "license_plate": "99-XYZ-1",
#         "make": "Tesla",
#         "model": "Model 3",
#         "color": "White",
#         "year": "2022",
#     }

#     response = requests.post(
#         f"{BASE_URL}/vehicles",
#         json=ValidVehicle,
#         headers=headers1,
#     )
#     assert response.status_code == 201
#     vehicle_data = response.json()
#     vehicle_id = vehicle_data["vehicle"]["id"]

#     response = requests.get(f"{BASE_URL}/vehicles")
#     assert response.status_code == 401

#     response = requests.get(f"{BASE_URL}/vehicles", headers=headers1)
#     assert response.status_code == 200
#     vehicles_list = response.json()
#     assert isinstance(vehicles_list, list)

#     found = None
#     for v in vehicles_list:
#         if v["id"] == vehicle_id:
#             found = v
#             break

#     assert found is not None
#     assert found["license_plate"] == ValidVehicle["license_plate"]
#     assert found["make"] == ValidVehicle["make"]
#     assert found["model"] == ValidVehicle["model"]
#     assert found["color"] == ValidVehicle["color"]
#     assert str(found["year"]) == str(ValidVehicle["year"])

#     response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers1)
#     assert response.status_code == 200
#     v = response.json()
#     assert v["id"] == vehicle_id
#     assert v["license_plate"] == ValidVehicle["license_plate"]
#     assert v["make"] == ValidVehicle["make"]
#     assert v["model"] == ValidVehicle["model"]
#     assert v["color"] == ValidVehicle["color"]
#     assert str(v["year"]) == str(ValidVehicle["year"])

#     response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers2)
#     assert response.status_code == 403
