# import uuid
# import requests
# from DataAccesLayer.db_utils_users import load_users, update_user_data, delete
# import pytest
# import random

# BASE_URL = "http://localhost:8000"

# def create_user(user_data):
#     requests.post(f"{BASE_URL}/register", json=user_data)

#     login = requests.post(f"{BASE_URL}/login", json=user_data)
#     if login.status_code != 200:
#         raise RuntimeError(f"Login failed ({login.status_code}): {login.text}")

#     return login.json()


# def register_Admin(user_data):
#     requests.post(f"{BASE_URL}/register", json=user_data)

#     admin = load_users()[-1]
#     admin.role = "ADMIN"
#     update_user_data(admin)


# def login(user_data):
#     login = requests.post(f"{BASE_URL}/login", json=user_data)
#     if login.status_code != 200:
#         raise RuntimeError(f"Login failed ({login.status_code}): {login.text}")

#     return login.json()

# def test_user_get_history_self():
#     DummyUser = {
#     "username": f"sezeven_{random.randint(1000,9999)}",
#     "password": "Password321!",
#     "name": "sezeven Hashemy",
#     "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#     "phone": f"+999{random.randint(100000000, 999999999)}",
#     "birth_year": 2000
# }

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
#         "username": f"userone_test_user_get_history_other_user{random.randint(1000,9999)}",
#         "password": "Password321!",
#         "name": "Test D. Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
#         "birth_year": 1969
#     }

#     DummyUserTwo = {
#         "username": f"usertwo_test_user_get_history_other_user{random.randint(1000,9999)}",
#         "password": "Password321!",
#         "name": "Test D. Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
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
#         "username": f"admin_test_admin_get_history_other_user{random.randint(1000,9999)}",
#         "password": "Password321!",
#         "name": "Test D. Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
#         "birth_year": 1969
#     }

#     DummyUser = {
#         "username": f"user_test_admin_get_history_other_user{random.randint(1000,9999)}",
#         "password": "Password321!",
#         "name": "Test D. Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
#         "birth_year": 1969
#     }

#     admin_data = create_user(DummyAdmin)

#     admin = next((user for user in load_users() if user.id == admin_data.get("user_id")))
#     admin.role = "ADMIN"
#     update_user_data(admin)

#     admin_data = create_user(DummyAdmin)
#     auth = { "Authorization": admin_data.get("session_token") }

# # BASE_URL = "http://localhost:8000"

# # def create_user(user_data):
# #     reg = requests.post(f"{BASE_URL}/register", json=user_data)
# #     if reg.status_code not in (200, 201):
# #         raise RuntimeError(f"Registration failed ({reg.status_code}): {reg.text}")

# #     login = requests.post(f"{BASE_URL}/login", json=user_data)
# #     if login.status_code != 200:
# #         raise RuntimeError(f"Login failed ({login.status_code}): {login.text}")

# #     return login.json()

#     delete(admin_data.get("user_id"))
#     delete(user_data.get("user_id"))
# def test_user_get_history_self():
#     DummyUser = {
#         "username": f"user_test_user_get_history_self_{random.randint(1000,9999)}",
#         "password": "Password123!",
#         "name": "Test D Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
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
#         "username": f"userone_test_user_get_history_other_user{random.randint(1000,9999)}",
#         "password": "Password123!!",
#         "name": "Test D Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
#         "birth_year": 1969
#     }

#     DummyUserTwo = {
#         "username": f"usertwo_test_user_get_history_other_user{random.randint(1000,9999)}",
#         "password": "Password123!!",
#         "name": "Test D Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
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
#         "username": f"admin_test_admin_get_history_other_user{random.randint(1000,9999)}",
#         "password": "Password123!!",
#         "name": "Test D Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
#         "birth_year": 1969
#     }

#     DummyUser = {
#         "username": f"user_test_admin_get_history_other_user{random.randint(1000,9999)}",
#         "password": "Password123!!",
#         "name": "Test D Ummy",
#         "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
#         "phone": f"+999{random.randint(100000000, 999999999)}",
#         "birth_year": 1969
#     }

#     register_Admin(DummyAdmin)

#     admin_data = login(DummyAdmin)

#     auth = { "Authorization": admin_data.get("session_token") }

#     user_data = create_user(DummyUser)

#     response = requests.get(f"{BASE_URL}/history/{user_data.get("user_id")}", headers=auth)

#     assert response.status_code == 200

#     delete(admin_data.get("user_id"))
#     delete(user_data.get("user_id"))
