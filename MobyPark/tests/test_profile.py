import requests
import pytest

BASE_URL = "http://localhost:8000"

def test_profile_put():
    dummyuser = {
        "username": "dummy123",
        "password": "d123",
        "name": "dummy"
    }
    requests.post(f"{BASE_URL}/register", json=dummyuser)

    login_result = requests.post(f"{BASE_URL}/login", json={
        "username": "dummy123",
        "password": "d123"
    })

    assert login_result.status_code == 200

    login_data = login_result.json()
    token = login_data["session_token"]

    updated_dummy = {
        "name": "Samuel Updated",
        "password": "newpassword"
    }

    update_result = requests.put(f"{BASE_URL}/profile", json=updated_dummy, headers={"Authorization": token})

    assert update_result.status_code == 200
    assert update_result.text == "User updated successfully"

    result_noToken = requests.put(f"{BASE_URL}/profile",json=updated_dummy)

    assert result_noToken.status_code == 401
    assert result_noToken.text == "Unauthorized: Invalid or missing session token"

def test_profile_get():
    dummyuser = {
        "username": "newdummy123",
        "password": "newd123",
        "name": "newdummy"
    }

    requests.post(f"{BASE_URL}/register", json=dummyuser)

    login_result = requests.post(f"{BASE_URL}/login", json={
        "username": "newdummy123",
        "password": "newd123"
    })

    assert login_result.status_code == 200

    login_data = login_result.json()
    token = login_data["session_token"]

    result_with_token = requests.get(f"{BASE_URL}/profile", headers={"Authorization": token})

    assert result_with_token.status_code == 200

    result_noToken = requests.get(f"{BASE_URL}/profile", json = dummyuser)

    assert result_noToken.status_code == 401

