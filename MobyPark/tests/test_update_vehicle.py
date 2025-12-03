# import requests
# import pytest

# BASE_URL = "http://localhost:8000"


# def get_session_token(user_data):
#     response = requests.post(f"{BASE_URL}/login", json=user_data)
#     return response.json().get("session_token")


# def test_put_vehicles_endpoint():
#     DummyUserOne = {
#         "username": "vehicle_user_one_put",
#         "password": "321",
#         "name": "Vehicle User One PUT",
#         "email": "vehicle_user_one_put@gmail.com",
#         "phone": "+31022290000",
#         "birth_year": 2000
#     }

#     ValidVehicle = {
#         "license_plate": "99-XYZ-1",
#         "make": "Tesla",
#         "model": "Model 3",
#         "color": "White",
#         "year": "2022"
#     }

#     IncompleteUpdate = {
#         "license_plate": "11-AAA-1",
#         "make": "Tesla",
#         "model": "Model S",
#         "year": "2023"
#     }

#     UpdatedVehicle = {
#         "license_plate": "11-AAA-1",
#         "make": "Tesla",
#         "model": "Model S",
#         "color": "Black",
#         "year": "2023"
#     }

#     requests.post(f"{BASE_URL}/register", json=DummyUserOne)
#     token1 = get_session_token(DummyUserOne)
#     headers1 = {"Authorization": token1}

#     response = requests.post(f"{BASE_URL}/vehicles", json=ValidVehicle, headers=headers1)
#     assert response.status_code == 201

#     vehicle_data = response.json()
#     vehicle_id = vehicle_data["vehicle"]["id"]

#     response = requests.put(
#         f"{BASE_URL}/vehicles/{vehicle_id}",
#         json=IncompleteUpdate,
#         headers=headers1
#     )
#     assert response.status_code == 400
#     data = response.json()
#     assert data["error"] == "Required field missing"
#     assert data["field"] == "color"

#     response = requests.put(
#         f"{BASE_URL}/vehicles/{vehicle_id}",
#         json=UpdatedVehicle,
#         headers=headers1
#     )
#     assert response.status_code == 200

#     updated_data = response.json()
#     assert updated_data["status"] == "Updated"
#     assert updated_data["vehicle"]["id"] == vehicle_id
#     assert updated_data["vehicle"]["license_plate"] == UpdatedVehicle["license_plate"]
#     assert updated_data["vehicle"]["make"] == UpdatedVehicle["make"]
#     assert updated_data["vehicle"]["model"] == UpdatedVehicle["model"]
#     assert updated_data["vehicle"]["color"] == UpdatedVehicle["color"]
#     assert str(updated_data["vehicle"]["year"]) == str(UpdatedVehicle["year"])
