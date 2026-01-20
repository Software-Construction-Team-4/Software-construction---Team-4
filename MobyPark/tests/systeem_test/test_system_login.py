import time
import requests
import pytest
import random

BASE_URL = "http://127.0.0.1:8000"

random_user = {
    "username": f"sezeven_{random.randint(1000,9999)}",
    "password": "Sez677!!",
    "name": "sezeven Hashemy",
    "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
    "phone": f"+310{random.randint(100000000, 999999999)}",
    "birth_year": 2000
}

def wait_for_server(url, timeout=30):
    start = time.time()
    while True:
        try:
            requests.get(url, timeout=5)
            return
        except requests.exceptions.RequestException:
            if time.time() - start > timeout:
                pytest.fail(f"Server not responding at {url}")
            time.sleep(1)

@pytest.fixture
def registered_user():
    wait_for_server(BASE_URL)
    for attempt in range(5):
        try:
            resp = requests.post(f"{BASE_URL}/register", json=random_user, timeout=15)
            if resp.status_code == 201:
                return random_user
        except requests.exceptions.RequestException:
            pass
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
