# import uuid
# import requests
# from DataAccesLayer.db_utils_users import load_users, update_user_data, delete
# import pytest

# BASE_URL = "http://localhost:8000"

# def create_user(user_data):
#     reg = requests.post(f"{BASE_URL}/register", json=user_data)
#     if reg.status_code not in (200, 201):
#         raise RuntimeError(f"Registration failed ({reg.status_code}): {reg.text}")

#     login = requests.post(f"{BASE_URL}/login", json=user_data)
#     if login.status_code != 200:
#         raise RuntimeError(f"Login failed ({login.status_code}): {login.text}")

#     return login.json()

# def test_user_get_history_self():
#     DummyUser = {
#         "username": f"user_test_user_get_history_self_{uuid.uuid4()}",
#         "password": "123",
#         "name": "Test D. Ummy",
#         "email": "test_user_get_history_self@test.com",
#         "phone": "+31 06 00000000",
#         "birth_year": 1969
#     }

#     user_data = create_user(DummyUser)
#     auth = { "Authorization": user_data.get("session_token") }

#     payload = { "parking_lot_id": 1, "licenseplate": "000-000-000" }
#     requests.post(f"{BASE_URL}/parking-lots/sessions/start", json=payload, headers=auth)
#     requests.post(f"{BASE_URL}/parking-lots/sessions/stop", json=payload, headers=auth)

#     response = requests.get(f"{BASE_URL}/history", headers=auth)

#     assert response.status_code == 200

#     body = response.json()
#     assert len(body["history"]) > 0

#     delete(user_data.get("user_id"))

# def test_user_get_history_other_user():
#     DummyUserOne = {
#         "username": "userone_test_user_get_history_other_user",
#         "password": "123",
#         "name": "Test D. Ummy",
#         "email": "test_user_get_history_other_user@test-one.com",
#         "phone": "+31 06 00000001",
#         "birth_year": 1969
#     }

#     DummyUserTwo = {
#         "username": "usertwo_test_user_get_history_other_user",
#         "password": "123",
#         "name": "Test D. Ummy",
#         "email": "test_user_get_history_other_user@test-two.com",
#         "phone": "+31 06 00000002",
#         "birth_year": 1969
#     }

#     user_data_one = create_user(DummyUserOne)
#     auth = { "Authorization": user_data_one.get("session_token") }

#     user_data_two = create_user(DummyUserTwo)

#     response = requests.get(f"{BASE_URL}/history/{user_data_two.get("user_id")}", headers=auth)

#     assert response.status_code == 401

#     delete(user_data_one.get("user_id"))
#     delete(user_data_two.get("user_id"))

# def test_admin_get_history_other_user():
#     DummyAdmin = {
#         "username": "admin_test_admin_get_history_other_user",
#         "password": "123",
#         "name": "Test D. Ummy",
#         "email": "test_admin_get_history_other_user@test-admin.com",
#         "phone": "+31 06 00000001",
#         "birth_year": 1969
#     }

#     DummyUser = {
#         "username": "user_test_admin_get_history_other_user",
#         "password": "123",
#         "name": "Test D. Ummy",
#         "email": "test_admin_get_history_other_user@test.com",
#         "phone": "+31 06 00000002",
#         "birth_year": 1969
#     }

#     admin_data = create_user(DummyAdmin)

#     admin = next((user for user in load_users() if user.id == admin_data.get("user_id")))
#     admin.role = "ADMIN"
#     update_user_data(admin)

#     admin_data = create_user(DummyAdmin)
#     auth = { "Authorization": admin_data.get("session_token") }

#     user_data = create_user(DummyUser)

#     response = requests.get(f"{BASE_URL}/history/{user_data.get("user_id")}", headers=auth)

#     assert response.status_code == 200

#     delete(admin_data.get("user_id"))
#     delete(user_data.get("user_id"))
