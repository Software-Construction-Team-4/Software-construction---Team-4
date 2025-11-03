# import requests
# import pytest

# BASE_URL = "http://localhost:8000"

# def test_logout():
#     dummyuser = {
#         "username": "logoutDummy",
#         "password": "logout123",
#         "name": "Logout Dummy"
#     }

#     requests.post(f"{BASE_URL}/register", json=dummyuser)

#     login_result = requests.post(f"{BASE_URL}/login", json={
#         "username": "logoutDummy",
#         "password": "logout123"
#     })

#     assert login_result.status_code == 200

#     login_data = login_result.json()
#     token = login_data["session_token"]

#     logout_result = requests.get(f"{BASE_URL}/logout", headers={"Authorization": token})

#     assert logout_result.status_code == 200
#     assert logout_result.text == "User logged out"

#     result_noToken = requests.get(f"{BASE_URL}/logout")

#     assert result_noToken.status_code == 400
#     assert result_noToken.text == "Invalid session token"