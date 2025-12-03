# import requests
# import pytest
# import uuid

# BASE_URL = "http://localhost:8000"


# def get_session_token(user_data):
#     response = requests.post(f"{BASE_URL}/login", json=user_data)
#     return response.json().get("session_token")


# def make_unique_user():
#     """
#     Create a user payload with a random suffix so each test run
#     gets a fresh user with no existing vehicles in the DB.
#     """
#     suffix = uuid.uuid4().hex[:8]
#     return {
#         "username": f"vehicle_user_one_{suffix}",
#         "password": "321",
#         "name": "Vehicle User One",
#         "email": f"vehicle_user_one_{suffix}@gmail.com",
#         "phone": "+31022290000",
#         "birth_year": 2000,
#     }


# def test_post_vehicles_endpoint():
#     DummyUserOne = make_unique_user()

#     IncompleteVehicle = {
#         "license_plate": "99-XYZ-1",
#         "make": "Tesla",
#         "model": "Model 3",
#         "year": "2022",
#     }

#     ValidVehicle = {
#         "license_plate": "99-XYZ-1",
#         "make": "Tesla",
#         "model": "Model 3",
#         "color": "White",
#         "year": "2022",
#     }

#     requests.post(f"{BASE_URL}/register", json=DummyUserOne)
#     token1 = get_session_token(DummyUserOne)
#     headers1 = {"Authorization": token1}

#     response = requests.post(f"{BASE_URL}/vehicles", json=IncompleteVehicle, headers=headers1)
#     assert response.status_code == 400
#     data = response.json()
#     assert data["error"] == "Missing required fields"
#     assert "color" in data["fields"]

#     response = requests.post(f"{BASE_URL}/vehicles", json=ValidVehicle, headers=headers1)
#     assert response.status_code == 201

#     vehicle_data = response.json()
#     assert vehicle_data["status"] == "Success"
#     assert vehicle_data["vehicle"]["license_plate"] == ValidVehicle["license_plate"]
#     assert vehicle_data["vehicle"]["make"] == ValidVehicle["make"]
#     assert vehicle_data["vehicle"]["model"] == ValidVehicle["model"]
#     assert vehicle_data["vehicle"]["color"] == ValidVehicle["color"]
#     assert str(vehicle_data["vehicle"]["year"]) == str(ValidVehicle["year"])

#     vehicle_id = vehicle_data["vehicle"]["id"]

#     response = requests.post(f"{BASE_URL}/vehicles", json=ValidVehicle, headers=headers1)
#     assert response.status_code == 409
#     data = response.json()
#     assert data["error"] == "User already has a vehicle"

