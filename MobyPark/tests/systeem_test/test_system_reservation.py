import requests
import pytest
import random
from datetime import datetime, timedelta

from DataAccesLayer.db_utils_users import delete as delete_user

BASE_URL = "http://127.0.0.1:8001"
TEST_PARKING_LOT_ID = 1588


def iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


random_user = {
    "username": f"sezeven_{random.randint(1000,9999)}",
    "password": "Sez677!!",
    "name": "sezeven Hashemy",
    "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
    "phone": f"+310{random.randint(100000000, 999999999)}",
    "birth_year": 2000
}

register_response = requests.post(f"{BASE_URL}/register", json=random_user, timeout=5)
if register_response.status_code != 201:
    pytest.fail(f"User registration failed: {register_response.status_code} {register_response.text}")


@pytest.fixture(scope="module")
def user_session():
    r = requests.post(
        f"{BASE_URL}/login",
        json={"username": random_user["username"], "password": random_user["password"]},
        timeout=5
    )
    assert r.status_code == 200, r.text
    data = r.json()
    return data["session_token"], data["user_id"]


@pytest.fixture(scope="module", autouse=True)
def cleanup_user(user_session):
    yield
    _, user_id = user_session
    try:
        delete_user(int(user_id))
    except Exception:
        pass


def test_login_success():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": random_user["username"], "password": random_user["password"]},
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
        json={"username": random_user["username"], "password": "wrong"},
        timeout=5
    )
    assert response.status_code in (400, 401, 403)


def test_verkeerde_route():
    response = requests.get(f"{BASE_URL}/this-route-does-not-exist", timeout=5)
    assert response.status_code == 404


def test_create_reservation_no_auth():
    start = datetime.now() + timedelta(days=2)
    end = start + timedelta(hours=2)

    r = requests.post(
        f"{BASE_URL}/reservations",
        json={
            "start_time": iso(start),
            "end_time": iso(end),
            "parking_lot_id": 1588,
            "cost": 10.0
        },
        timeout=5
    )
    assert r.status_code == 401


def test_create_vehicle(user_session):
    token, _ = user_session

    vehicle_payload = {
        "license_plate": f"TS{random.randint(10,99)}-{random.randint(100,999)}-X",
        "make": "Toyota",
        "model": "Yaris",
        "color": "Blue",
        "year": 2020
    }

    v = requests.post(
        f"{BASE_URL}/vehicles",
        headers={"Authorization": token},
        json=vehicle_payload,
        timeout=5
    )

    assert v.status_code in (201, 200), v.text

    if v.status_code == 201:
        data = v.json()
        assert data["status"] == "Success"
        assert "vehicle" in data


def test_reservation_good(user_session):
    token, _ = user_session

    start = datetime.now() + timedelta(days=3)
    end = start + timedelta(hours=2)

    r_create = requests.post(
        f"{BASE_URL}/reservations",
        headers={"Authorization": token},
        json={
            "parking_lot_id": 1588,
            "start_time": iso(start),
            "end_time": iso(end),
            "cost": 12.5,
            "status": "pending"
        },
        timeout=5
    )

    assert r_create.status_code == 201, r_create.text
    created = r_create.json()
    assert created["status"] == "Success"
    rid = created["reservation"]["id"]

    r_get = requests.get(
        f"{BASE_URL}/reservations/{rid}",
        headers={"Authorization": token},
        timeout=5
    )
    assert r_get.status_code == 200, r_get.text
    res = r_get.json()
    assert str(res["id"]) == str(rid)

    new_start = start + timedelta(hours=1)
    new_end = end + timedelta(hours=1)

    r_put = requests.put(
        f"{BASE_URL}/reservations/{rid}",
        headers={"Authorization": token},
        json={"start_time": iso(new_start), "end_time": iso(new_end)},
        timeout=5
    )
    assert r_put.status_code == 200, r_put.text
    upd = r_put.json()
    assert upd["status"] == "Updated"
    assert "reservation" in upd
