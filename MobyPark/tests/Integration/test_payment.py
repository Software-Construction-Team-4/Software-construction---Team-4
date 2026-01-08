import os
import random
import requests
import pytest
import session_calculator as sc

from DataAccesLayer.PaymentsAccess import PaymentsDataAccess
from DataAccesLayer.db_utils_users import delete

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def register_and_login():
    user = {
        "username": f"sezeven_{random.randint(1000, 9999)}",
        "password": "Password321!",
        "name": "sezeven Hashemy",
        "email": f"sezeven{random.randint(1000, 9999)}@gmail.com",
        "phone": f"+999{random.randint(100000000, 999999999)}",
        "birth_year": 2000
    }

    r = requests.post(f"{BASE_URL}/register", json=user)
    assert r.status_code == 201, f"User registration failed {r.status_code}: {r.text}"

    login = requests.post(f"{BASE_URL}/login", json=user)
    assert login.status_code == 200, f"Login failed {login.status_code}: {login.text}"
    data = login.json()

    headers = {"Authorization": data["session_token"]}
    user_id = data["user_id"]
    return user, headers, user_id


@pytest.fixture
def auth():
    user, headers, user_id = register_and_login()
    yield user, headers, user_id
    delete(user_id)


@pytest.fixture
def created_payment(auth):
    user, headers, user_id = auth

    base_payment = {
        "parking_lot_id": str(random.randint(1, 1500)),
        "session_id": str(random.randint(1, 10000)),
        "license_plate": f"TEST-{random.randint(100, 999)}",
        "amount": random.randint(1, 1000),
        "bank": "ING",
        "payment_methode": "paypal",
    }

    response = requests.post(
        f"{BASE_URL}/payments",
        json=base_payment,
        headers=headers
    )

    assert response.status_code == 201, f"Create payment failed {response.status_code}: {response.text}"
    payment = response.json()

    yield payment, base_payment, headers

    PaymentsDataAccess().delete_payment(payment["payment_id"])


def test_POST_payment(created_payment):
    payment, base_payment, headers = created_payment
    assert payment["status"] == "Success"
    assert "payment_id" in payment


def test_GET_payment(auth):
    user, headers, user_id = auth

    response = requests.get(
        f"{BASE_URL}/payments",
        headers=headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_PUT_payment(created_payment):
    payment, base_payment, headers = created_payment
    payment_id = payment["payment_id"]

    put_payload = {
        "bank": "ING",
        "issuer_code": "CXE287BP",
        "payment_method": "paypal",
        "transaction_hash": sc.generate_transaction_validation_hash(
            base_payment["session_id"],
            base_payment["license_plate"]
        )
    }

    response = requests.put(
        f"{BASE_URL}/payments/{payment_id}",
        json=put_payload,
        headers=headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "Success"


def test_POST_payment_sad(auth):
    user, headers, user_id = auth

    wrong_payment = {
        "parking_lot_id": str(random.randint(1, 1500)),
        "session_id": str(random.randint(1, 10000)),
        "license_plate": f"TEST-{random.randint(100, 999)}",
    }

    response = requests.post(
        f"{BASE_URL}/payments",
        json=wrong_payment,
        headers=headers
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error"] == "Require field missing"
    assert data["field"] in {"amount", "bank", "payment_methode"}


def test_PUT_payment_sad(created_payment):
    payment, base_payment, headers = created_payment
    payment_id = payment["payment_id"]

    wrong_put_payment = {
        "bank": "ING",
        "issuer_code": "CXE287BP",
        "payment_method": "paypal",
        "transaction_hash": ""
    }

    response = requests.put(
        f"{BASE_URL}/payments/{payment_id}",
        json=wrong_put_payment,
        headers=headers
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"] == "Validation failed"
    assert body["id"] == payment_id

    response2 = requests.put(
        f"{BASE_URL}/payments/{-10}",
        json=wrong_put_payment,
        headers=headers
    )

    assert response2.status_code == 404
    assert response2.text == "Payment not found!"

    wrong_put_payment2 = {
        "bank": "ING",
        "issuer_code": "CXE287BP",
        "payment_method": "paypal",
    }

    response3 = requests.put(
        f"{BASE_URL}/payments/{payment_id}",
        json=wrong_put_payment2,
        headers=headers
    )

    assert response3.status_code == 401
    assert response3.json()["error"] == "Require field missing"
    assert response3.json()["field"] == "transaction_hash"
