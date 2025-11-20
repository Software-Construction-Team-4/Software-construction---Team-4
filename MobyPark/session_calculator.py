from datetime import datetime
from DataAccesLayer.PaymentsAccess import PaymentsDataAccess
from hashlib import md5
import math
import uuid


def load_payment_data():
    payments = PaymentsDataAccess().get_all_payments()  # list[PaymentsModel]
    return [
        {
            "transaction": p.transaction_hash,  # or p.payment_hash
            "amount": float(p.amount),
        }
        for p in payments
    ]

def calculate_price(parkinglot, sid, data):
    price = 0
    start = datetime.strptime(data["started"], "%d-%m-%Y %H:%M:%S")

    if data.get("stopped"):
        end = datetime.strptime(data["stopped"], "%d-%m-%Y %H:%M:%S")
    else:
        end = datetime.now()

    diff = end - start
    hours = math.ceil(diff.total_seconds() / 3600)

    if diff.total_seconds() < 180:
        price = 0
    elif end.date() > start.date():
        price = float(parkinglot.get("daytariff", 999)) * (diff.days + 1)
    else:
        price = float(parkinglot.get("tariff")) * hours
        if price > float(parkinglot.get("daytariff", 999)):
            price = float(parkinglot.get("daytariff", 999))

    return price, hours, diff.days + 1 if end.date() > start.date() else 0


def generate_payment_hash(sid, data):
    raw = f"{sid}{data['licenseplate']}"
    return md5(raw.encode("utf-8")).hexdigest()


def generate_transaction_validation_hash():
    return str(uuid.uuid4())


def check_payment_amount(tx_hash):
    payments = load_payment_data()
    total = 0.0

    for payment in payments:
        if payment["transaction"] == tx_hash:
            total += payment["amount"]

    return total
