import json
from datetime import datetime, timedelta
from session_manager import get_session
from LogicLayer.reservationsLogic import get_reservation, create_reservation, update_reservation_logic, delete_reservation_logic, process_missed_sessions
from DataModels.reservationsModel import Reservations
from DataAccesLayer.db_utils_parkingLots import update_parking_lot, parking_lot_exists
from DataAccesLayer.vehicle_access import VehicleAccess

def send_json(self, status_code, data):
    self.send_response(status_code)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

def require_session(self):
    token = self.headers.get("Authorization")
    session_user = get_session(token)
    if not session_user:
        send_json(self, 401, {"error": "Unauthorized"})
        return None
    return session_user

def do_GET(self):
    if self.path.startswith("/reservations/"):
        rid = self.path.replace("/reservations/", "")
        reservation = get_reservation(rid)
        if not reservation:
            return send_json(self, 404, {"error": "Reservation not found"})

        session_user = require_session(self)
        if not session_user: return

        if session_user.get("role") != "ADMIN" and reservation.user_id != session_user.get("user_id"):
            return send_json(self, 403, {"error": "Access denied"})

        send_json(self, 200, reservation.to_dict())

def do_POST(self):
    if self.path == "/reservations":
        session_user = require_session(self)
        if not session_user: return

        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        for field in ["start_time", "end_time", "parking_lot_id"]:
            if field not in data:
                return send_json(self, 400, {"error": f"{field} missing"})

        if not parking_lot_exists(data["parking_lot_id"]):
            return send_json(self, 404, {"error": "Parking lot not found"})

        vehicles = VehicleAccess.get_all_user_vehicles(session_user.get("user_id"))
        if not vehicles:
            return send_json(self, 404, {"error": "User is not registered to any vehicle"})

        new_res = Reservations(
            id=None,
            user_id=session_user.get("user_id"),
            parking_lot_id=data["parking_lot_id"],
            vehicle_id=vehicles[0].id,
            start_time=data["start_time"],
            end_time=data["end_time"],
            status="pending",
            created_at=datetime.now(),
            cost=None,
            updated_at=None
        )
        create_reservation(new_res)
        send_json(self, 201, {"status": "Success", "reservation": new_res.to_dict()})

def do_PUT(self):
    if self.path.startswith("/reservations/"):
        rid = self.path.replace("/reservations/", "")
        session_user = require_session(self)
        if not session_user: return

        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
        reservation = get_reservation(rid)
        if not reservation:
            return send_json(self, 404, {"error": "Reservation not found"})

        if session_user.get("role") != "ADMIN" and reservation.user_id != session_user.get("user_id"):
            return send_json(self, 403, {"error": "Access denied"})

        for key in ["start_time", "end_time", "status", "cost"]:
            if key in data:
                setattr(reservation, key, data[key])

        if "status" in data:
            old_status = reservation.status
            new_status = data["status"]
            if old_status != "confirmed" and new_status == "confirmed":
                update_parking_lot(reservation.parking_lot_id, {"reserved": 1})
            elif old_status == "confirmed" and new_status != "confirmed":
                update_parking_lot(reservation.parking_lot_id, {"reserved": -1})

        update_reservation_logic(reservation)
        send_json(self, 200, {"status": "Updated", "reservation": reservation.to_dict()})

def do_DELETE(self):
    if self.path.startswith("/reservations/"):
        rid = self.path.replace("/reservations/", "")
        session_user = require_session(self)
        if not session_user: return

        reservation = get_reservation(rid)
        if not reservation:
            return send_json(self, 404, {"error": "Reservation not found"})

        if session_user.get("role") != "ADMIN" and reservation.user_id != session_user.get("user_id"):
            return send_json(self, 403, {"error": "Access denied"})

        if (reservation.start_time - datetime.now()).total_seconds() < 86400:
            return send_json(self, 403, {"error": "Cannot cancel <24h before start"})

        if reservation.status == "confirmed":
            update_parking_lot(reservation.parking_lot_id, {"reserved": -1})

        reservation.status = "canceled"
        update_reservation_logic(reservation)
        send_json(self, 200, {"status": "Canceled"})
