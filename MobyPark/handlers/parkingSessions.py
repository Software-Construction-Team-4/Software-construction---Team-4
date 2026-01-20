import json
from LogicLayer.sessionLogic import start_parking_session, stop_parking_session, load_sessions_for_user
from session_manager import get_session
from LogicLayer.reservationsLogic import get_reservation_by_user_id, update_reservation_logic
from DataAccesLayer.vehicle_access import VehicleAccess
from LogicLayer.lotsLogic import get_lot_with_id

#asdasd
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

        user_id = session_user.get("user_id")
        sessions = load_sessions_for_user(user_id)

        response = {}
        for item in sessions:
            response[str(item.id)] = {
                "id": item.id,
                "parking_lot_id": item.parking_lot_id,
                "user_id": item.user_id,
                "licenseplate": item.licenseplate,
                "started": item.started,
                "stopped": item.stopped,
                "duration_minutes": item.duration_minutes,
                "cost": item.cost,
                "payment_status": item.payment_status,
            }

        send_json(self, 200, response)
        return

    send_json(self, 404, {"error": "Invalid route"})


def do_POST(self):
    parts = self.path.strip("/").split("/")

    if parts[:3] == ["parking-lots", "sessions", "start"]:
        token = self.headers.get("Authorization")
        session_user = get_session(token) if token else None
        if not session_user:
            send_json(self, 401, {"error": "Unauthorized"})
            return

        reservation = get_reservation_by_user_id(session_user.get("user_id"))

        data = {}
        if reservation is None:
            content_length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(content_length))

        vehicles = VehicleAccess.get_all_user_vehicles(session_user.get("user_id"))
        if not vehicles:
            send_json(self, 403, {"error": "You are not registered to any car"})
            return

        parking_lot_id = reservation["parking_lot_id"] if reservation else data.get("parking_lot_id")

        parking_lot = get_lot_with_id(parking_lot_id)
        
        if parking_lot["capacity"] <= (parking_lot["active_sessions"] + parking_lot["reserved"]):
            send_json(self, 201, {"message": "The parking lot has reached it's capacity"})
            return

        result = start_parking_session(
            parking_lot_id,
            vehicles[0].license_plate,
            session_user.get("user_id")
        )

        if not result.get("ok"):
            send_json(self, 409, result)
            return

        if reservation:
            reservation.status = "confirmed"
            update_reservation_logic(reservation)

        send_json(self, 201, {"message": "Your session has started"})
        return

    if parts[:3] == ["parking-lots", "sessions", "stop"]:
        token = self.headers.get("Authorization")
        session_user = get_session(token) if token else None
        if not session_user:
            send_json(self, 401, {"error": "Unauthorized"})
            return

        session = stop_parking_session(session_user.get("user_id"))
        if not session:
            send_json(self, 404, {"error": "No active session found"})
            return

        send_json(self, 200, {"success": "Parking session stopped", "id": session.id})
        return

    send_json(self, 404, {"error": "Invalid route"})
