from datetime import datetime, timedelta
from typing import Union
from DataAccesLayer.PaymentsAccess import PaymentsDataAccess
from hashlib import sha256
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

def calculate_price(parkinglot, data) -> tuple[float, float, int]:
    start_date: Union[str, datetime] = data["started"]
    if not isinstance(start_date, datetime):
        start_date = datetime.strptime(data["started"], "%d-%m-%Y %H:%M:%S")

    stop_date: Union[str, datetime] = data.get("stopped") or datetime.now()
    if not isinstance(stop_date, datetime):
        stop_date = datetime.strptime(data["stopped"], "%d-%m-%Y %H:%M:%S")

    diff: timedelta = stop_date - start_date

    hours: float = diff.total_seconds() / 3600
    days: int = diff.days

    hour_tariff: float = float(parkinglot.get("tariff", 5.00))
    day_tariff: float = float(parkinglot.get("daytariff", 100.00))

    if diff.total_seconds() < 180: # parked for less than three minutes
        return 0.00, hours, days
    elif stop_date.date() > start_date.date(): # parked for over a day, with one day running from 00:00 to 23:59
        days = min(diff.days, 1)
        price: float = day_tariff * days
        return price, hours, days
    else:
        price: float = min(hour_tariff * hours, day_tariff) # capped at the daily tariff
        return price, hours, days


def generate_transaction_validation_hash(sid, licenseplate):
    text = str(sid) + str(licenseplate).strip()
    return sha256(text.encode("utf-8")).hexdigest()



def generate_payment_hash():
    return str(uuid.uuid4())


def check_payment_amount(tx_hash):
    data_access = PaymentsDataAccess()

    payment = data_access.get_by_transaction_hash(tx_hash)
    return float(payment.amount)
