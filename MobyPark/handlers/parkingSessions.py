import json
from DataAccesLayer.db_utils_parkingSessions import start_session, stop_session, load_sessions
from session_manager import get_session


def send_json(self, status_code, data):
    self.send_response(status_code)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(data, default=str).encode("utf-8"))


def _unauthorized(self):
    send_json(self, 401, {"error": "Unauthorized"})


def _bad_request(self, message="Missing data"):
    send_json(self, 400, {"error": message})


def _get_authenticated_user(self):
    token = self.headers.get("Authorization")
    if not token:
        return None
    return get_session(token)


def _is_admin(session_user: dict) -> bool:
    return bool(session_user) and session_user.get("role") == "ADMIN"


def _same_user_id(a, b) -> bool:

    return a is not None and b is not None and str(a) == str(b)


def do_GET(self):
    parts = self.path.strip("/").split("/")

    if parts[0] == "parking-lots" and len(parts) > 1 and parts[1] == "sessions":
        lot_id = parts[2] if len(parts) == 3 else None
        sessions = load_sessions(lot_id)

        sessions_serialized = {}
        for sid, s in sessions.items():
            # Non-admins only see their own sessions
            if not admin and not _same_user_id(s.user_id, current_user_id):
                continue

            sessions_serialized[sid] = {
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

        content_length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(content_length))
        except Exception:
            send_json(self, 400, {"error": "Invalid JSON"})
            return

        parking_lot_id = data.get("parking_lot_id")
        licenseplate = data.get("licenseplate")
        if not parking_lot_id or not licenseplate:
            send_json(self, 400, {"error": "Missing data"})
            return

        result = start_session(parking_lot_id, licenseplate, session_user.get("user_id"))

        if not result.get("ok"):
            send_json(self, 409, result)
            return

        # send_json(self, 201, {"session_id": result["session_id"]})
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

        parking_lot_id = data.get("parking_lot_id")
        licenseplate = data.get("licenseplate")
        if not parking_lot_id or not licenseplate:
            send_json(self, 400, {"error": "Missing data"})
            return

        session = stop_session(parking_lot_id, licenseplate) 
        if not session:
            send_json(self, 404, {"error": "No active session found for this plate in this parking lot"})
            return

        session_dict = {
            "id": session.id,
            "parking_lot_id": session.parking_lot_id,
            "user_id": session.user_id,
            "licenseplate": session.licenseplate,
            "started": session.started,
            "stopped": session.stopped,
            "duration_minutes": session.duration_minutes,
            "cost": session.cost,
            "payment_status": session.payment_status,
        }
        send_json(self, 200, session_dict)
        return

    send_json(self, 404, {"error": "Invalid route"})
