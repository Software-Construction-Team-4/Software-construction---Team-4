import json
from DataAccesLayer.db_utils_parkingSessions import start_session, stop_session, load_sessions
from session_manager import get_session

def do_GET(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) > 1 and parts[1] == "sessions":
        lot_id = parts[2] if len(parts) == 3 else None
        sessions = load_sessions(lot_id)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(sessions).encode("utf-8"))
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")

def do_POST(self):
    parts = self.path.strip("/").split("/")

    if len(parts) == 3 and parts[0] == "parking-lots" and parts[1] == "sessions" and parts[2] == "start":
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized")
            return

        session_user = get_session(token)
        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))

        parking_lot_id = data.get("parking_lot_id")
        licenseplate = data.get("licenseplate")
        if not parking_lot_id or not licenseplate:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Missing data")
            return

        session_id = start_session(parking_lot_id, licenseplate, session_user.get("user_id"))

        if session_id is None:
            self.send_response(409)  # Conflict
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Active session already exists for this license plate in this parking lot"
            }).encode("utf-8"))
            return

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"session_id": session_id}).encode("utf-8"))
        return

    if len(parts) == 3 and parts[0] == "parking-lots" and parts[1] == "sessions" and parts[2] == "stop":
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))

        parking_lot_id = data.get("parking_lot_id")
        licenseplate = data.get("licenseplate")
        if not parking_lot_id or not licenseplate:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Missing data")
            return

        session = stop_session(parking_lot_id, licenseplate)
        if session:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(session).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"No active session")
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")
