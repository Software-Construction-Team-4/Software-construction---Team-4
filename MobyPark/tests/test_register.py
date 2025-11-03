# import requests
# import pytest

# BASE_URL = "http://localhost:8000"

# def test_register_endpoint():
#     DummyUser ={
#         "username": "sam123",
#         "password": "s123",
#         "name": "Sam"
#     }
        
#     FirstResult = requests.post(f"{BASE_URL}/register", json = DummyUser)

#     assert FirstResult.status_code == 201
#     assert FirstResult.text == "User created"

#     SecondResult = requests.post(f"{BASE_URL}/register", json = DummyUser)

#     assert SecondResult.status_code == 200
#     assert SecondResult.text == "Username already taken"