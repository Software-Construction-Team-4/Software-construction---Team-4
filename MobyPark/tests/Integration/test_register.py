import requests
import pytest
from DataAccesLayer.db_utils_users import delete
import random

import os
from environment import Environment
BASE_URL = Environment.get_var("BASE_URL", "http://localhost:8000")

def test_register_endpoint():
    DummyUser = {
        "username": f"sezeven_{random.randint(1000,9999)}",
        "password": "Sez677!!",
        "name": "sezeven Hashemy",
        "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
        "phone": f"+310{random.randint(100000000, 999999999)}",
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