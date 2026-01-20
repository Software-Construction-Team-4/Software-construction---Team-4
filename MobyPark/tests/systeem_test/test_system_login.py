import time
import requests
import pytest
import random
import uuid

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture
def registered_user():
    unique_user = {
        "username": f"sezeven_{uuid.uuid4().hex[:8]}",
        "password": "Sez677!!",
        "name": "sezeven Hashemy",
        "email": f"{uuid.uuid4().hex[:8]}@gmail.com",
        "phone": f"+310{random.randint(100000000, 999999999)}",
        "birth_year": 2000
    }

    for attempt in range(5):
        try:
            resp = requests.post(f"{BASE_URL}/register", json=unique_user, timeout=15)
            print(f"Attempt {attempt+1}: {resp.status_code} - {resp.text}")
            if resp.status_code == 201:
                return unique_user
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1}: Exception - {e}")
        time.sleep(2)

    pytest.fail("User registration failed after 5 attempts")


def test_login_success(registered_user):
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        },
        timeout=5
    )

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "User logged in"
    assert "session_token" in data
    assert "user_id" in data

def test_login_wrong_password(registered_user):
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": registered_user["username"], "password": "wrong"},
        timeout=15
    )

    assert response.status_code in (400, 401, 403)


def test_unknown_route():
    response = requests.get(
        f"{BASE_URL}/this-route-does-not-exist",
        timeout=15
    )

    assert response.status_code == 404
