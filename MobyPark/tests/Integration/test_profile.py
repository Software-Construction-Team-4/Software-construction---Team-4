import requests
import pytest
from DataAccesLayer.db_utils_users import delete

import os
from environment import Environment
BASE_URL = Environment.get_var("BASE_URL", "http://localhost:8000")

def test_profile_put():
    dummyuser = {
        "username": "sina",
        "password": "Sina321!!",
        "name": "Sina Hashemy",
        "email": "sina@gmail.com",
        "phone": "+310222939422",
        "birth_year": 2000
    }
    requests.post(f"{BASE_URL}/register", json=dummyuser)

    login_result = requests.post(f"{BASE_URL}/login", json={
        "username": "sina",
        "password": "Sina321!!"
    })

    assert login_result.status_code == 200

    login_data = login_result.json()
    token = login_data["session_token"]

    updated_dummy = {
        "id": login_data["user_id"],
        "username": "sam",
        "password": "Sam321!!"
    }

    update_result = requests.put(f"{BASE_URL}/profile", json=updated_dummy, headers={"Authorization": token})

    assert update_result.status_code == 200
    assert update_result.text == "User updated successfully"

    result_noToken = requests.put(f"{BASE_URL}/profile",json=updated_dummy)

    assert result_noToken.status_code == 401
    assert result_noToken.text == "Unauthorized: Invalid or missing session token"

    FirstResult = requests.post(f"{BASE_URL}/login", json = updated_dummy)
    data = FirstResult.json()
    user_id = data.get("user_id")

    delete(user_id)

def test_profile_get():
    dummyuser = {
        "username": "sam",
        "password": "Sam321!!",
        "name": "Sam Hashemy",
        "email": "sam@gmail.com",
        "phone": "+310222939422",
        "birth_year": 2000
    }

    requests.post(f"{BASE_URL}/register", json=dummyuser)

    login_result = requests.post(f"{BASE_URL}/login", json={
        "username": "sam",
        "password": "Sam321!!"
    })

    data = login_result.json()
    user_id = data.get("user_id")

    assert login_result.status_code == 200

    login_data = login_result.json()
    token = login_data["session_token"]

    result_with_token = requests.get(f"{BASE_URL}/profile", headers={"Authorization": token})

    assert result_with_token.status_code == 200

    result_noToken = requests.get(f"{BASE_URL}/profile", json = dummyuser)

    assert result_noToken.status_code == 401

    delete(user_id)

