import requests
import pytest
from DataAccesLayer.db_utils_users import delete

import os
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
print("BASE_URL used by tests:", BASE_URL)

def test_login_endpoint():
    DummyUserOne ={
        "username": "sina",
        "password": "Sina321!!",
        "name": "Sina Hashemy",
        "email": "sina@gmail.com",
        "phone": "+310222939422",
        "birth_year": 2000
    }

    DummyUserTwo ={
        "username": "sina",
        "password": "Sina3211!!",
        "name": "Sina Hashemy",
        "email": "sina@gmail.com",
        "phone": "+310222939422",
        "birth_year": 2000
    }

    DummyUserThree ={
        "username": "NietBestaand",
        "password": "Sina3211!!",
        "name": "Sina Hashemy",
        "email": "sina@gmail.com",
        "phone": "+310222939422",
        "birth_year": 2000
    }

    requests.post(f"{BASE_URL}/register", json = DummyUserOne)

    FirstResult = requests.post(f"{BASE_URL}/login", json = DummyUserOne)
    data = FirstResult.json()
    user_id = data.get("user_id")

    assert FirstResult.status_code == 200
    assert data["message"] == "User logged in"

    SecondResult = requests.post(f"{BASE_URL}/login", json = DummyUserTwo)

    assert SecondResult.status_code == 401
    assert SecondResult.text == "Invalid credentials"

    delete(user_id)  # delte staat hier sinds tweede check de user nodig heeft die in eerste check(test) is gemaakt

    ThirdResult = requests.post(f"{BASE_URL}/login", json = DummyUserThree)

    assert ThirdResult.status_code == 401
    assert ThirdResult.text == "User not found"

