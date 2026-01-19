import requests
import uuid
import random
import pytest
from DataAccesLayer.db_utils_parkingLots import save_parking_lot, delete_parking_lot
import os

from environment import Environment
BASE_URL = Environment.get_var("BASE_URL", "http://localhost:8000")

def get_session_token(user_data):
    resp = requests.post(f"{BASE_URL}/login", json=user_data)
    return resp.json()

def create_dummy_admin_user():
    username = uuid.uuid4().hex[:8]
    random_phonenumber = random.randint(100000000, 999999999)
    dummy_user = {
        "username": username,
        "password": "Password321!",
        "name": "Admin User",
        "email": f"{username}@test.com",
        "phone": f"+310{random_phonenumber}",
        "birth_year": 2000
    }

    requests.post(f"{BASE_URL}/register", json=dummy_user)

    import mysql.connector
    conn = mysql.connector.connect(
        host=Environment.get_var("DB_HOST"),
        port=int(Environment.get_var("DB_PORT")),
        user=Environment.get_var("DB_USER"),
        password=Environment.get_var("DB_PASSWORD"),
        database=Environment.get_var("DB_NAME")
    )
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role='ADMIN' WHERE username=%s", (username,))
    conn.commit()
    cursor.close()
    conn.close()

    session_data = get_session_token(dummy_user)
    token = session_data["session_token"]
    user_id = session_data["user_id"]
    headers = {"Authorization": token}
    return headers, user_id

def create_dummy_parking_lot_data():
    random_number = random.randint(1, 999)
    return {
        "name": f"TestLot{random_number}",
        "location": "Test City",
        "address": f"{random_number} Test Street",
        "capacity": 50,
        "reserved": 0,
        "tariff": 5,
        "daytariff": 20,
        "latitude": 52.0 + random.random(),
        "longitude": 13.0 + random.random(),
        "status": "open"
    }

def test_create_parking_lot_happy_path():
    headers, user_id = create_dummy_admin_user()
    lot_data = create_dummy_parking_lot_data()

    resp = requests.post(f"{BASE_URL}/parking-lots", json=lot_data, headers=headers)
    assert resp.status_code == 201
    lot_id = resp.json()["id"]

    delete_parking_lot(lot_id)

def test_update_parking_lot_happy_path():
    headers, user_id = create_dummy_admin_user()
    lot_data = create_dummy_parking_lot_data()
    lot_id = save_parking_lot(lot_data)

    updated_data = {"capacity": lot_data["capacity"] + 10, "status": "closed"}
    resp = requests.put(f"{BASE_URL}/parking-lots/{lot_id}", json=updated_data, headers=headers)
    assert resp.status_code == 200

    delete_parking_lot(lot_id)

def test_delete_parking_lot_happy_path():
    headers, user_id = create_dummy_admin_user()
    lot_data = create_dummy_parking_lot_data()
    lot_id = save_parking_lot(lot_data)

    resp = requests.delete(f"{BASE_URL}/parking-lots/{lot_id}", headers=headers)
    assert resp.status_code == 200

def test_create_parking_lot_unauthorized_sad_path():
    lot_data = create_dummy_parking_lot_data()
    resp = requests.post(f"{BASE_URL}/parking-lots", json=lot_data)
    assert resp.status_code == 401
    assert "Unauthorized" in resp.text

def test_update_parking_lot_unauthorized_sad_path():
    lot_data = create_dummy_parking_lot_data()
    lot_id = save_parking_lot(lot_data)
    updated_data = {"capacity": 100}

    resp = requests.put(f"{BASE_URL}/parking-lots/{lot_id}", json=updated_data)
    assert resp.status_code == 401
    assert "Unauthorized" in resp.text

    delete_parking_lot(lot_id)

def test_delete_parking_lot_unauthorized_sad_path():
    lot_data = create_dummy_parking_lot_data()
    lot_id = save_parking_lot(lot_data)

    resp = requests.delete(f"{BASE_URL}/parking-lots/{lot_id}")
    assert resp.status_code == 401
    assert "Unauthorized" in resp.text

    delete_parking_lot(lot_id)
