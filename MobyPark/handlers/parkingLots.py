import json
from LogicLayer.lotsLogic import (
    load_parking_lots,
    load_parking_lot_by_id
)
from DataAccesLayer.db_utils_parkingLots import (
    save_parking_lot,
    update_parking_lot,
    delete_parking_lot
)
from . import parkingSessions
from session_manager import get_session

def send_json(self, status_code, data):
    self.send_response(status_code)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

def require_session(self):
    token = self.headers.get("Authorization")
    if not token or not get_session(token):
        self.send_response(401)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b"Unauthorized: Invalid or missing session token")
        return None
    return get_session(token)

def require_admin(self, session_user):
    if session_user.get("role") != "ADMIN":
        self.send_response(403)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b"Access denied")
        return False
    return True

def lot_to_public_dict(lot):
    lot_data = lot.__dict__

    capacity = int(lot_data.get("capacity", 0) or 0)
    active_sessions = int(lot_data.get("active_sessions", 0) or 0)
    reserved_spots = int(lot_data.get("reserved", 0) or 0)

    return {
        "name": lot_data.get("name"),
        "location": lot_data.get("location"),
        "address": lot_data.get("address"),
        "spaces_left": max(capacity - active_sessions - reserved_spots, 0),
        "tariff": lot_data.get("tariff"),
        "daytariff": lot_data.get("daytariff"),
    }
