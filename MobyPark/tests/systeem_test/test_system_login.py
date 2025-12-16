#DIT IS AI!!

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_login_success():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": "tt", "password": "321"},
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
        json={"username": "tt", "password": "wrong"},
        timeout=5
    )

    assert response.status_code in (400, 401, 403)


def test_unknown_route():
    response = requests.get(
        f"{BASE_URL}/this-route-does-not-exist",
        timeout=5
    )

    assert response.status_code == 404
