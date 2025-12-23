import requests
import pytest
from DataAccesLayer.db_utils_users import delete

BASE_URL = "http://localhost:8000"

def test_logout():
    dummyuser = {
        "username": "siADDoiena",
        "password": "Sina321!!",
        "name": "Sina Hashemy",
        "email": "sinTESdbwuba@gmail.com",
        "phone": "+310211139422",
        "birth_year": 2000
    }

    requests.post(f"{BASE_URL}/register", json=dummyuser)

    login_result = requests.post(f"{BASE_URL}/login", json={
        "username": "siADDoiena",
        "password": "Sina321!!"
    })

    data = login_result.json()
    user_id = data.get("user_id")

    assert login_result.status_code == 200

    login_data = login_result.json()
    token = login_data["session_token"]

    logout_result = requests.get(f"{BASE_URL}/logout", headers={"Authorization": token})

    assert logout_result.status_code == 200
    assert logout_result.text == "User logged out"

    result_noToken = requests.get(f"{BASE_URL}/logout")

    assert result_noToken.status_code == 400
    assert result_noToken.text == "Invalid session token"

    delete(user_id)