import requests
import pytest
import random

from DataAccesLayer.PaymentsAccess import PaymentsDataAccess, PaymentsModel

import handlers.payments

BASE_URL = "http://localhost:8000"

def get_session_token(user_data):
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    return response.json()


random_user = {
    "username": f"sezeven{random.random()}",
    "password": "321",
    "name": "sezeven Hashemy",
    "email": "sezeven@gmail.com",
    "phone": "+31022293944",
    "birth_year": 2000
}

random_base_payment = { 
    "parking_lot_id": f"{random.randint(1, 10000)}", 
    "session_id": f"{random.randint(1, 10000)}", 
    "license_plate": f"TEST-{random.randint(1, 999)}", 
    "amount": random.randint(1, 10000)
}

random_put_payment = {
    "amount": 100,
    "bank": "ING",
    "date": "4-12-2025",
    "issuer_code": "CXE287BP",
    "payment_method": "paypal",
    "transaction_hash": "3e05a53d8a8a6666871800cbc317fa6e"
}

def test_POST_payment():
    return

def test_GET_payment():
    return

def test_PUT_payment():
    return

def test_DELETE_payment():
    return
