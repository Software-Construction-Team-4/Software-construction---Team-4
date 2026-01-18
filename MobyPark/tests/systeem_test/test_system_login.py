

import requests
import uuid
import pytest
import requests
import random

from DataAccesLayer.vehicle_access import VehicleAccess
from DataAccesLayer.db_utils_users import delete as delete_user

from environment import Environment
BASE_URL = Environment.get_var("BASE_URL", "http://localhost:8000")


random_user = {
    "username": f"sezeven_{random.randint(1000,9999)}",
    "password": "Sez677!!",
    "name": "sezeven Hashemy",
    "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
    "phone": f"+310{random.randint(100000000, 999999999)}",
    "birth_year": 2000
}

register_response = requests.post(f"{BASE_URL}/register", json=random_user)

if register_response.status_code != 201:
    pytest.fail("User registration failed")

def test_login_success():
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": random_user["username"],
            "password": random_user["password"]
        },
        timeout=5
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "User logged in"
    assert "session_token" in data
    assert "user_id" in data

def test_login_wrong_password():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": random_user["username"], "password": "wrong"},
        timeout=5
    )

    assert response.status_code in (400, 401, 403)


def test_unknown_route():
    response = requests.get(
        f"{BASE_URL}/this-route-does-not-exist",
        timeout=5
    )

    assert response.status_code == 404
