import datetime
from decimal import Decimal

class ParkingLot:
    def __init__(self, id: int, name: str, location: str, address: str, capacity: int, active_sessions: int, reserved: int, tariff: Decimal, daytariff: Decimal, 
                 created_at: datetime.date, latitude: Decimal, longitude: Decimal, status: str, closed_reason: str, closed_date: datetime.date):
        self.id = id
        self.name = name
        self.location = location
        self.address = address
        self.capacity = capacity
        self.active_sessions = active_sessions
        self.reserved = reserved
        self.tariff = tariff
        self.daytariff = daytariff
        self.created_at = created_at
        self.latitude = latitude
        self.longitude = longitude
        self.status = status
        self.closed_reason = closed_reason
        self.closed_date = closed_date
