import requests
import pytest
import random
import uuid
import string
import os
import json

from DataModels.vehicle_model import VehicleModel
from DataAccesLayer.PaymentsAccess import PaymentsDataAccess
from DataAccesLayer.db_utils_parkingSessions import delete_parking_session_by_id, get_db_connection
from DataAccesLayer.vehicle_access import VehicleAccess
from DataAccesLayer.db_utils_users import delete

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    return response.json()


def test_post_payment_endpoint():
    username = uuid.uuid4().hex[:8]
    random_phonenumber = random.randint(100000000, 999999999)
    random_number_one = random.randint(10, 99)
    random_number_two = random.randint(1, 9)
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))

    DummyUser = {
        "username": username,
        "password": "Password321!",
        "name": "sezeven Hashemy",
        "email": f"sezeven{username}@gmail.com",
        "phone": f"+310{random_phonenumber}",
        "birth_year": 2000
    }

    DummyVehicle = {
        "license_plate": f"{random_number_one}-{random_letters}-{random_number_two}",
        "make": "Ford",
        "model": "Sport",
        "color": "Red",
        "year": "2020"
    }

    DummyPayment = {
        "bank": "ABN",
        "payment_method": "ideal"
    }

    IncorrectDummyPayment = {
        "bank": "ABN"
    }

    AdminLogin = {
        "username": "baas",
        "password": "Sina321!!",
    }

    requests.post(f"{BASE_URL}/register", json=DummyUser)

    user_data = get_session_token(DummyUser)
    user_id = user_data["user_id"]
    token = user_data["session_token"]
    headers = {"Authorization": token}

    vehicle_response = requests.post(f"{BASE_URL}/vehicles", json=DummyVehicle, headers=headers)
    vehicle_data = vehicle_response.json()["vehicle"]
    vehicle_obj = VehicleModel(**vehicle_data)

    requests.post(f"{BASE_URL}/parking-lots/sessions/start", json={"parking_lot_id": 5}, headers=headers)

    payment_error_one = requests.post(f"{BASE_URL}/payments", json=DummyPayment, headers=headers)
    assert payment_error_one.status_code == 402
    assert payment_error_one.text.strip() == "You have no parking session that needs to be paid"

    parking_session_stop = requests.post(f"{BASE_URL}/parking-lots/sessions/stop", headers=headers)
    parking_session_data = parking_session_stop.json()
    parking_session_id = parking_session_data["id"]

    payment_error_two = requests.post(f"{BASE_URL}/payments", json=IncorrectDummyPayment, headers=headers)
    assert payment_error_two.status_code == 401
    assert payment_error_two.json()["error"] == "Require field missing"

    payment = requests.post(f"{BASE_URL}/payments", json=DummyPayment, headers=headers)
    assert payment.status_code == 201

    payment_data = payment.json()
    assert payment_data["status"] == "Success"


    admin_data = get_session_token(AdminLogin)
    admin_id = admin_data["user_id"]
    token2 = admin_data["session_token"]
    headers2 = {"Authorization": token2}

    refund_error_one = requests.post(f"{BASE_URL}/payments/refund", json={"id": admin_id}, headers=headers)
    assert refund_error_one.status_code == 403
    assert refund_error_one.text == "Access denied"

    refund_error_two = requests.post(f"{BASE_URL}/payments/refund", json={"wrong_field": admin_id}, headers=headers2)
    assert refund_error_two.status_code == 401
    assert refund_error_two.text == "error: Require field missing, field: id"

    refund = requests.post(f"{BASE_URL}/payments/refund", json={"id": payment_data["payment_id"]}, headers=headers2)
    assert refund.status_code == 201
    assert refund.text == "succes: The user has been refunded"

    payments_del = PaymentsDataAccess()
    payments_del.delete_payment(payment_data["payment_id"])
    connection = get_db_connection()
    delete_parking_session_by_id(connection, parking_session_id)
    VehicleAccess.delete(vehicle_obj)
    delete(user_id)