# import requests
# import pytest
# import uuid

# BASE_URL = "http://localhost:8000"


# def get_session_token(user_data):
#     response = requests.post(f"{BASE_URL}/login", json=user_data)
#     return response.json().get("session_token")


# def unique_user(base_name):

#     suffix = uuid.uuid4().hex[:6]
#     return f"{base_name}_{suffix}"


# def test_delete_vehicles_endpoint():

#     NormalUser = {
#         "username": unique_user("vehicle_user_delete"),
#         "password": "321",
#         "name": "Vehicle User Delete",
#         "email": f"{unique_user('vehicle_user_delete')}@gmail.com",
#         "phone": "+31022290000",
#         "birth_year": 2000
#     }

#     AdminUser = {
#         "username": unique_user("admin_user_delete"),
#         "password": "321",
#         "name": "Admin Delete",
#         "email": f"{unique_user('admin_user_delete')}@gmail.com",
#         "phone": "+31022290010",
#         "birth_year": 1990,
#         "role": "ADMIN"
#     }

#     ValidVehicle = {
#         "license_plate": "DEL-123",
#         "make": "BMW",
#         "model": "X5",
#         "color": "Black",
#         "year": "2021"
#     }

#     requests.post(f"{BASE_URL}/register", json=NormalUser)
#     token_normal = get_session_token(NormalUser)
#     headers_normal = {"Authorization": token_normal}

#     response = requests.post(f"{BASE_URL}/vehicles", json=ValidVehicle, headers=headers_normal)
#     assert response.status_code == 201
#     vehicle_id = response.json()["vehicle"]["id"]

#     response = requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers_normal)
#     assert response.status_code == 403

#     requests.post(f"{BASE_URL}/register", json=AdminUser)
#     token_admin = get_session_token(AdminUser)
#     headers_admin = {"Authorization": token_admin}

#     response = requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers_admin)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "Deleted"

#     response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}", headers=headers_admin)
#     assert response.status_code == 404
