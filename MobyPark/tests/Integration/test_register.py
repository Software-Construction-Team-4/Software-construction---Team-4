import requests
import pytest
from DataAccesLayer.db_utils_users import delete

import os
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def test_register_endpoint():
    DummyUser ={
        "username": "test",
        "password": "Test321!",
        "name": "test Hashemy",
        "email": "test@gmail.com",
        "phone": "+310222939422",
        "birth_year": 2000
    }

        
    FirstResult = requests.post(f"{BASE_URL}/register", json = DummyUser)

    assert FirstResult.status_code == 201
    assert FirstResult.text == "User created"

    SecondResult = requests.post(f"{BASE_URL}/register", json = DummyUser)

    assert SecondResult.status_code == 400
    assert SecondResult.text == "Username already taken"

    FirstResult = requests.post(f"{BASE_URL}/login", json = DummyUser)
    data = FirstResult.json()
    user_id = data.get("user_id")

    delete(user_id)