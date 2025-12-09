import requests
from DataAccesLayer.db_utils_users import load_users, update_user_data, delete
import pytest

BASE_URL = "http://localhost:8000"

def create_user(user_data):
    requests.post(f"{BASE_URL}/register", json=user_data)

    response = requests.post(f"{BASE_URL}/login", json=user_data)
    return response.json()

def test_user_get_history_self():
    DummyUser = {
        "username": "user",
        "password": "123",
        "name": "Test D. Ummy",
        "email": "me@test.com",
        "phone": "+31 06 00000000",
        "birth_year": 1969
    }

    user_data = create_user(DummyUser)
    auth = { "Authorization": user_data.get("session_token") }

    requests.post(f"{BASE_URL}/parking-lots/sessions/start", json={ "parking_lot_id": 1, "licenseplate": "000-000-000" }, headers=auth)

    response = requests.get(f"{BASE_URL}/history/{user_data.get("user_id")}", headers=auth)

    assert response.status_code == 200

    body = response.json()
    assert len(body.history) > 0

    delete(user_data.get("user_id"))

def test_user_get_history_other_user():
    DummyUserOne = {
        "username": "user_one",
        "password": "123",
        "name": "Test D. Ummy",
        "email": "me@test-one.com",
        "phone": "+31 06 00000001",
        "birth_year": 1969
    }

    DummyUserTwo = {
        "username": "user_two",
        "password": "123",
        "name": "Test D. Ummy",
        "email": "me@test-two.com",
        "phone": "+31 06 00000002",
        "birth_year": 1969
    }

    user_data_one = create_user(DummyUserOne)
    auth = { "Authorization": user_data_one.get("session_token") }

    user_data_two = create_user(DummyUserTwo)

    response = requests.get(f"{BASE_URL}/history/{user_data_two.get("user_id")}", headers=auth)

    assert response.status_code == 401

    delete(user_data_one.get("user_id"))
    delete(user_data_two.get("user_id"))

def test_admin_get_history_other_user():
    DummyAdmin = {
        "username": "user_one",
        "password": "123",
        "name": "Test D. Ummy",
        "email": "me@test-one.com",
        "phone": "+31 06 00000001",
        "birth_year": 1969
    }

    DummyUser = {
        "username": "user_two",
        "password": "123",
        "name": "Test D. Ummy",
        "email": "me@test-two.com",
        "phone": "+31 06 00000002",
        "birth_year": 1969
    }

    admin_data = create_user(DummyAdmin)
    auth = { "Authorization": admin_data.get("session_token") }

    admin = next((user for user in load_users() if user.id == admin_data.get("user_id")))
    admin.role = "ADMIN"
    update_user_data(admin)

    user_data = create_user(DummyUser)

    response = requests.get(f"{BASE_URL}/history/{user_data.get("user_id")}", headers=auth)

    assert response.status_code == 200

    delete(admin_data.get("user_id"))
    delete(user_data.get("user_id"))
