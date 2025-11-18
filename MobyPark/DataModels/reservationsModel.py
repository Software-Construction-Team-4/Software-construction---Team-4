import datetime
from decimal import Decimal

class Reservations:
    def __init__(self, id: int, user_id: int, parking_lot_id: int, vehicle_id: int, start_time: datetime.datetime, 
                 end_time: datetime.datetime, status: str, created_at: datetime.datetime, cost: Decimal, updated_at: datetime.date):
        self.id = id
        self.user_id = user_id
        self.parking_lot_id = parking_lot_id
        self.vehicle_id = vehicle_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.created_at = created_at
        self.cost = cost
        self.updated_at = updated_at
