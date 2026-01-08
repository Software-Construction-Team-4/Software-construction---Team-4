import json
import requests
from DataAccesLayer.db_utils_parkingSessions import start_session, stop_session, update_payment_status, load_sessions_by_userID
from session_manager import get_session
from DataAccesLayer.db_utils_reservations import get_reservation_by_user_id, update_status_only
from DataAccesLayer.vehicle_access import VehicleAccess
from LogicLayer.paymentsLogic import paymentsLogic
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def send_json(self, status_code, data):
    self.send_response(status_code)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(data, default=str).encode("utf-8"))


def do_GET(self):
    parts = self.path.strip("/").split("/")

    if parts[0] == "parking-lots" and len(parts) > 1 and parts[1] == "sessions":
        token = self.headers.get("Authorization")
        session_user = get_session(token) if token else None
        if not session_user:
            send_json(self, 401, {"error": "Unauthorized"})
            return

        current_user_id = session_user.get("user_id")
        
        sessions = load_sessions_by_userID(current_user_id)

        sessions_serialized = {}
        for s in sessions:
            sessions_serialized[str(s.id)] = {
                "id": s.id,
                "parking_lot_id": s.parking_lot_id,
                "user_id": s.user_id,
                "licenseplate": s.licenseplate,
                "started": s.started,
                "stopped": s.stopped,
                "duration_minutes": s.duration_minutes,
                "cost": s.cost,
                "payment_status": s.payment_status,
            }

        send_json(self, 200, sessions_serialized)
        return

    send_json(self, 404, {"error": "Invalid route"})




def do_POST(self):
    parts = self.path.strip("/").split("/")

    if len(parts) == 3 and parts[0] == "parking-lots" and parts[1] == "sessions" and parts[2] == "start":
        token = self.headers.get("Authorization")
        session_user = get_session(token) if token else None
        if not session_user:
            send_json(self, 401, {"error": "Unauthorized"})
            return
        
        reservation = get_reservation_by_user_id(session_user.get("user_id"))
        
        if(reservation == None):
            send_json(self, 403, {"error": "Cannot start parking session: no valid reservation found."})
            return
        
        vehicle = VehicleAccess.get_by_id(reservation["vehicle_id"])

        result = start_session(reservation["parking_lot_id"], vehicle.license_plate, session_user.get("user_id"))

        if not result.get("ok"):
            send_json(self, 409, result)
            return
        
        update_status_only(reservation["id"])

        send_json(self, 201, {"message": "Your session has started"})
        return

    if len(parts) == 3 and parts[0] == "parking-lots" and parts[1] == "sessions" and parts[2] == "stop":
        token = self.headers.get("Authorization")
        session_user = get_session(token) if token else None
        if not session_user:
            send_json(self, 401, {"error": "Unauthorized"})
            return
        
        content_length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(content_length))
        except Exception:
            send_json(self, 400, {"error": "Invalid JSON"})
            return
        
        bank = data.get("bank")
        pay_methode = data.get("payment_methode")
        if not bank or not pay_methode:
            send_json(self, 400, {"error": "Missing data"})
            return

        session = stop_session(session_user.get("user_id"))
        if not session:
            send_json(self, 404, {"error": "No active session found for this user"})
            return

        # deze create payment create is nog hard coded maar werkt( het is makkelijk om non hard coded te maken)
        paymentsLogic.create_payment( 
            session=session,
            amount=5,
            bank=bank,
            payment_method=pay_methode,
            initiator=session_user.get("user_id")
        )

        update_payment_status(session_user.get("user_id"))

        send_json(self, 200, {"Parking session has successfully stopped"})
        return

    send_json(self, 404, {"error": "Invalid route"})


