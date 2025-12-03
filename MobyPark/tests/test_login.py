import requests
import pytest

BASE_URL = "http://localhost:8000"

def test_login_endpoint():
    DummyUserOne ={
        "username": "sina",
        "password": "321",
        "name": "Sina Hashemy",
        "email": "sina@gmail.com",
        "phone": "+31022293944",
        "birth_year": 2000
    }

    DummyUserTwo ={
        "username": "sina",
        "password": "3211",
        "name": "Sina Hashemy",
        "email": "sina@gmail.com",
        "phone": "+31022293944",
        "birth_year": 2000
    }

    DummyUserThree ={
        "username": "NietBestaand",
        "password": "321",
        "name": "Sina Hashemy",
        "email": "sina@gmail.com",
        "phone": "+31022293944",
        "birth_year": 2000
    }

    requests.post(f"{BASE_URL}/register", json = DummyUserOne)

    FirstResult = requests.post(f"{BASE_URL}/login", json = DummyUserOne)

    data = FirstResult.json()
    assert FirstResult.status_code == 200
    assert data["message"] == "User logged in"

    SecondResult = requests.post(f"{BASE_URL}/login", json = DummyUserTwo)

    assert SecondResult.status_code == 401
    assert SecondResult.text == "Invalid credentials"

    ThirdResult = requests.post(f"{BASE_URL}/login", json = DummyUserThree)

    assert ThirdResult.status_code == 401
    assert ThirdResult.text == "User not found"