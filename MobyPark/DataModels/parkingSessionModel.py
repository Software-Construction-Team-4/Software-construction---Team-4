import datetime
from decimal import Decimal

class ParkingSession:
    def __init__(self, id: int, parking_lot_id: int, user_id: int, licenseplate: str, started: datetime.datetime, stopped: datetime.datetime, duration_minutes: int, cost: Decimal, payment_status: str, session: int):
        self.id = id
        self.parking_lot_id = parking_lot_id
        self.session = session
        self.user_id = user_id
        self.licenseplate = licenseplate
        self.started = started
        self.stopped = stopped
        self.duration_minutes = duration_minutes
        self.cost = cost
        self.payment_status = payment_status
