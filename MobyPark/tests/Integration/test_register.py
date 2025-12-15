# import requests
# import pytest

# BASE_URL = "http://localhost:8000"

# def test_register_endpoint():
#     DummyUser ={
#         "username": "test",
#         "password": "321",
#         "name": "test Hashemy",
#         "email": "test@gmail.com",
#         "phone": "+31022293942",
#         "birth_year": 2000
#     }

        
#     FirstResult = requests.post(f"{BASE_URL}/register", json = DummyUser)

#     assert FirstResult.status_code == 201
#     assert FirstResult.text == "User created"

#     SecondResult = requests.post(f"{BASE_URL}/register", json = DummyUser)

#     assert SecondResult.status_code == 200
#     assert SecondResult.text == "Username already taken"