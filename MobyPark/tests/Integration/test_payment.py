import requests
import pytest
import random
import session_calculator as sc

from DataAccesLayer.PaymentsAccess import PaymentsDataAccess
from DataAccesLayer.db_utils_users import delete

BASE_URL = "http://localhost:8000"



random_user = {
    "username": f"sezeven_{random.randint(1000,9999)}",
    "password": "Password321!",
    "name": "sezeven Hashemy",
    "email": f"sezeven{random.randint(1000,9999)}@gmail.com",
    "phone": f"+999{random.randint(100000000, 999999999)}",
    "birth_year": 2000
}

random_base_payment = { 
    "parking_lot_id": f"{random.randint(1, 1500)}", 
    "session_id": f"{random.randint(1, 10000)}", 
    "license_plate": f"TEST-{random.randint(100, 999)}", 
    "amount": random.randint(1, 1000)
}

random_put_payment = {
    "bank": "ING",
    "issuer_code": "CXE287BP",
    "payment_method": "paypal",
    "transaction_hash": sc.generate_transaction_validation_hash(
        random_base_payment["session_id"],
        random_base_payment["license_plate"]
    )
}

random_wrong_payment = { 
    "parking_lot_id": f"{random.randint(1, 1500)}", 
    "session_id": f"{random.randint(1, 10000)}", 
    "license_plate": f"TEST-{random.randint(100, 999)}", 
}

random_wrong_put_payment = {
    "bank": "ING",
    "issuer_code": "CXE287BP",
    "payment_method": "paypal",
    "transaction_hash": ""
}



def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)

    if response.status_code != 200:
        print("LOGIN FAILED", response.text)
        pytest.fail("Login failed")

    return response.json()

register_response = requests.post(f"{BASE_URL}/register", json=random_user)

if register_response.status_code != 201:
    pytest.fail(f"User registration failed {register_response.status_code}: {register_response.text}")

user_data = get_session_token(random_user)
token1 = user_data.get("session_token")
headers1 = {"Authorization": token1}




@pytest.fixture
def created_payment():
    response = requests.post(
        f"{BASE_URL}/payments",
        json=random_base_payment,
        headers=headers1
    )

    assert response.status_code == 201
    payment = response.json()

    yield payment

    PaymentsDataAccess().delete_payment(payment["payment_id"])
    delete(user_data.get("user_id"))

def test_POST_payment(created_payment):
    assert created_payment["status"] == "Success"
    assert "payment_id" in created_payment


def test_GET_payment():
    response = requests.get(
        f"{BASE_URL}/payments",
        headers=headers1
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_PUT_payment(created_payment):
    payment_id = created_payment["payment_id"]

    response = requests.put(
        f"{BASE_URL}/payments/{payment_id}",
        json=random_put_payment,
        headers=headers1
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Success"


#Sad paths
def test_POST_payment_sad():
    response = requests.post(
        f"{BASE_URL}/payments",
        json=random_wrong_payment,
        headers=headers1
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Require field missing"

def test_PUT_payment_sad(created_payment):
    payment_id = created_payment["payment_id"]

    response = requests.put(
        f"{BASE_URL}/payments/{payment_id}",
        json=random_wrong_put_payment,
        headers=headers1
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Validation failed"
    assert response.json()["id"] == payment_id

    response2 = requests.put(
        f"{BASE_URL}/payments/{-10}",
        json=random_wrong_put_payment,
        headers=headers1
    )

    assert response2.status_code == 404
    assert response2.text == "Payment not found!"

    del random_wrong_put_payment["transaction_hash"]

    response3 = requests.put(
        f"{BASE_URL}/payments/{payment_id}",
        json=random_wrong_put_payment,
        headers=headers1
    )

    assert response3.status_code == 401
    assert response3.json()["error"] == "Require field missing"




