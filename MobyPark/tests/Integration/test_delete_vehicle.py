# test_delete_vehicle.py

import requests
import pytest
import random
import uuid
import hashlib
from datetime import date

from DataAccesLayer.vehicle_access import VehicleAccess
from DataAccesLayer.db_utils_users import (
    delete as delete_user,
    save_user,
    load_users,
)
from DataModels.userModel import userModel

import os
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def make_unique_user(prefix: str):
    suffix = uuid.uuid4().hex[:8]
    return {
        "username": f"{prefix}_{suffix}",
        "password": "Password321!",
        "name": f"Test Name",
        "email": f"{prefix}_{suffix}@gmail.com",
        "phone": f"+310{random.randint(100000000, 999999999)}",
        "birth_year": 2000,
    }


def get_session_data(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)

    if response.status_code != 200:
        print("LOGIN FAILED", response.status_code, response.text)
        pytest.fail("Login failed")

    return response.json()


@pytest.fixture
def normal_and_admin_users():

    normal_user = make_unique_user("normal_user_delete")
    reg_normal = requests.post(f"{BASE_URL}/register", json=normal_user)
    if reg_normal.status_code != 201:
        pytest.fail(
            f"Normal user registration failed: "
            f"{reg_normal.status_code} {reg_normal.text}"
        )

    normal_data = get_session_data(normal_user)
    normal_token = normal_data.get("session_token")
    normal_user_id = normal_data.get("user_id")
    headers_normal = {"Authorization": normal_token}

    ValidVehicle = {
        "license_plate": "DEL-123",
        "make": "BMW",
        "model": "X5",
        "color": "Black",
        "year": "2021",
    }

    resp_vehicle = requests.post(
        f"{BASE_URL}/vehicles",
        json=ValidVehicle,
        headers=headers_normal,
    )
    assert resp_vehicle.status_code == 201
    vehicle_id = resp_vehicle.json()["vehicle"]["id"]


    admin_username = f"admin_delete_{uuid.uuid4().hex[:6]}"
    admin_password_plain = "321"
    admin_password_hashed = hashlib.sha256(admin_password_plain.encode()).hexdigest()

    admin_user_model = userModel(
        id=None,
        username=admin_username,
        password=admin_password_hashed,
        name="Admin Delete",
        email=f"{admin_username}@gmail.com",
        phone=f"+98{random.randint(10_000_000, 99_999_999)}",
        role="ADMIN",
        created_at=date.today().isoformat(),
        birth_year=1990,
        active=True,
    )

    save_user(admin_user_model)

    users = load_users()
    admin_from_db = next(u for u in users if u.username == admin_username)
    admin_user_id = admin_from_db.id

    admin_login_payload = {
        "username": admin_username,
        "password": admin_password_plain,
    }
    admin_data = get_session_data(admin_login_payload)
    admin_token = admin_data.get("session_token")
    headers_admin = {"Authorization": admin_token}

    yield {
        "headers_normal": headers_normal,
        "headers_admin": headers_admin,
        "normal_user_id": normal_user_id,
        "admin_user_id": admin_user_id,
        "vehicle_id": vehicle_id,
    }

    try:
        vehicles_normal = VehicleAccess.get_all_user_vehicles(normal_user_id)
        for v in vehicles_normal:
            VehicleAccess.delete(v)

        vehicles_admin = VehicleAccess.get_all_user_vehicles(admin_user_id)
        for v in vehicles_admin:
            VehicleAccess.delete(v)

        delete_user(normal_user_id)
        delete_user(admin_user_id)
    except Exception as e:
        print(f"[TEST CLEANUP ERROR] {e}")


def test_delete_vehicles_endpoint(normal_and_admin_users):
    headers_normal = normal_and_admin_users["headers_normal"]
    headers_admin = normal_and_admin_users["headers_admin"]
    vehicle_id = normal_and_admin_users["vehicle_id"]

    response = requests.delete(
        f"{BASE_URL}/vehicles/{vehicle_id}",
        headers=headers_normal,
    )
    assert response.status_code == 403

    response = requests.delete(
        f"{BASE_URL}/vehicles/{vehicle_id}",
        headers=headers_admin,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Deleted"

    response = requests.get(
        f"{BASE_URL}/vehicles/{vehicle_id}",
        headers=headers_admin,
    )
    assert response.status_code == 404
