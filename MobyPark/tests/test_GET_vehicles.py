# import requests
# import pytest

# BASE_URL = "http://localhost:8000"


# def get_session_token(user_data):
#     response = requests.post(f"{BASE_URL}/login", json=user_data)
#     return response.json().get("session_token")


# def test_get_vehicles_endpoint():
#     DummyUserOne = {
#         "username": "vehicle_user_one_get",
#         "password": "321",
#         "name": "Vehicle User One GET",
#         "email": "vehicle_user_one_get@gmail.com",
#         "phone": "+31022290000",
#         "birth_year": 2000
#     }

#     DummyUserTwo = {
#         "username": "vehicle_user_two_get",
#         "password": "321",
#         "name": "Vehicle User Two GET",
#         "email": "vehicle_user_two_get@gmail.com",
#         "phone": "+31022290001",
#         "birth_year": 2000
#     }

#     ValidVehicle = {
#         "license_plate": "99-XYZ-1",
#         "make": "Tesla",
#         "model": "Model 3",
#         "color": "White",
#         "year": "2022"
#     }

#     requests.post(f"{BASE_URL}/register", json=DummyUserOne)
#     token1 = get_session_token(DummyUserOne)
#     headers1 = {"Authorization": token1}

#     response = requests.post(f"{BASE_URL}/vehicles", json=ValidVehicle, headers=headers1)
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

#     requests.post(f"{BASE_URL}/register", json=DummyUserTwo)
#     token2 = get_session_token(DummyUserTwo)
#     headers2 = {"Authorization": token2}

#     response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers2)
#     assert response.status_code == 403
