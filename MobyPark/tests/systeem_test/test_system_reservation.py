import requests
import pytest
import random
import uuid
import string
import json
from datetime import datetime, timedelta

from DataAccesLayer.vehicle_access import VehicleAccess
from DataModels.vehicle_model import VehicleModel
from DataAccesLayer.db_utils_users import delete

import os
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8001")

TEST_PARKING_LOT_ID = 1


def iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def headers(token=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = token
    return h


def post(path, payload, token=None):
    return requests.post(
        f"{BASE_URL}{path}",
        headers=headers(token),
        data=json.dumps(payload),
        timeout=5
    )


def put(path, payload, token=None):
    return requests.put(
        f"{BASE_URL}{path}",
        headers=headers(token),
        data=json.dumps(payload),
        timeout=5
    )


def login(username: str, password: str):
    r = post("/login", {"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()


def test_reservations():
    username = uuid.uuid4().hex[:8]
    random_phonenumber = random.randint(100000000, 999999999)
    random_number_one = random.randint(10, 99)
    random_number_two = random.randint(1, 9)
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))

    dummy_user = {
        "username": username,
        "password": "Password321!",
        "name": "sezeven Hashemy",
        "email": f"sezeven{username}@gmail.com",
        "phone": f"+310{random_phonenumber}",
        "birth_year": 2000
    }

    dummy_vehicle = {
        "license_plate": f"{random_number_one}-{random_letters}-{random_number_two}",
        "make": "Ford",
        "model": "Sport",
        "color": "Red",
        "year": 2020
    }

    start = datetime.now() + timedelta(days=3)
    end = start + timedelta(hours=1)

    dummy_reservation = {
        "parking_lot_id": TEST_PARKING_LOT_ID,
        "start_time": iso(start),
        "end_time": iso(end),
        "cost": 14,
        "status": "pending"
    }

    reg = post("/register", dummy_user)
    assert reg.status_code == 201, reg.text

    session = login(dummy_user["username"], dummy_user["password"])
    user_id = session["user_id"]
    token = session["session_token"]

    r1 = post("/reservations", dummy_reservation, token=token)
    assert r1.status_code == 404, r1.text
    assert "vehicle" in r1.text.lower()

    v = post("/vehicles", dummy_vehicle, token=token)
    assert v.status_code in (201, 409), v.text

    vehicle_obj = None
    if v.status_code == 201:
        vehicle_dict = v.json()["vehicle"]
        vehicle_obj = VehicleModel(**vehicle_dict)

    r2 = post("/reservations", dummy_reservation, token=token)
    assert r2.status_code == 201, f"{r2.status_code} {r2.text}"

    reservation_id = r2.json()["reservation"]["id"]

    r_get = requests.get(
        f"{BASE_URL}/reservations/{reservation_id}",
        headers={"Authorization": token},
        timeout=5
    )
    assert r_get.status_code == 200, r_get.text
    current = r_get.json()

    new_start = start + timedelta(hours=1)
    new_end = end + timedelta(hours=1)

    put_payload = {
        "parking_lot_id": current["parking_lot_id"],
        "start_time": iso(new_start),
        "end_time": iso(new_end),
        "status": current["status"],
        "created_at": current["created_at"],
        "cost": current["cost"],
        "updated_at": current.get("updated_at")  # mag None zijn
    }

    r_put = put(f"/reservations/{reservation_id}", put_payload, token=token)
    assert r_put.status_code == 200, r_put.text

    try:
        requests.delete(
            f"{BASE_URL}/reservations/{reservation_id}",
            headers={"Authorization": token},
            timeout=5
        )
    except Exception:
        pass

    try:
        if vehicle_obj is not None:
            VehicleAccess.delete(vehicle_obj)
    except Exception:
        pass

    try:
        delete(user_id)
    except Exception:
        pass


def test_reservation_no_parking_lot():
    username = uuid.uuid4().hex[:8]
    random_phonenumber = random.randint(100000000, 999999999)

    dummy_user = {
        "username": username,
        "password": "Password321!",
        "name": "zevensez Hashemy",
        "email": f"zevensez{username}@gmail.com",
        "phone": f"+310{random_phonenumber}",
        "birth_year": 2000
    }

    reg = post("/register", dummy_user)
    assert reg.status_code == 201, reg.text

    session = login(dummy_user["username"], dummy_user["password"])
    user_id = session["user_id"]
    token = session["session_token"]

    dummy_vehicle = {
        "license_plate": f"ZZ-{random.randint(100,999)}-X",
        "make": "Ford",
        "model": "Sport",
        "color": "Red",
        "year": 2020
    }
    v = post("/vehicles", dummy_vehicle, token=token)
    assert v.status_code in (201, 409), v.text

    start = datetime.now() + timedelta(days=3)
    end = start + timedelta(hours=1)

    bad_reservation = {
        "parking_lot_id": 99999999,
        "start_time": iso(start),
        "end_time": iso(end),
        "cost": 14,
        "status": "pending"
    }

    r = post("/reservations", bad_reservation, token=token)
    assert r.status_code == 404, r.text

    try:
        delete(user_id)
    except Exception:
        pass
