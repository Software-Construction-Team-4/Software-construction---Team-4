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
from LogicLayer.sessionLogic import start_parking_session, stop_parking_session, load_sessions_for_user

import os
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8001")


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


def login(username: str, password: str):
    r = post("/login", {"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()


def test_parking_session_lifecycle():
    username = uuid.uuid4().hex[:8]
    random_phonenumber = random.randint(100000000, 999999999)

    dummy_user = {
        "username": username,
        "password": "Password321!",
        "name": "Sezeven Hashemy",
        "email": f"sezeven{username}@gmail.com",
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

    vehicle_obj = None
    if v.status_code == 201:
        vehicle_dict = v.json()["vehicle"]
        vehicle_obj = VehicleModel(**vehicle_dict)

    result = start_parking_session(
        parking_lot_id=1,
        licenseplate=dummy_vehicle["license_plate"],
        user_id=user_id
    )
    assert result.get("ok"), f"Failed to start session: {result}"

    session_id = result["session_id"]

    sessions = load_sessions_for_user(user_id)
    assert any(s.id == session_id for s in sessions), "Session not found for user"

    stopped_session = stop_parking_session(user_id)
    assert stopped_session is not None, "Failed to stop session"
    assert stopped_session.stopped is not None, "Stopped time not set"

    try:
        if vehicle_obj is not None:
            VehicleAccess.delete(vehicle_obj)
    except Exception:
        pass

    try:
        delete(user_id)
    except Exception:
        pass
