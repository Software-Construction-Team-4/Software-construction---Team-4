import json
from DataAccesLayer.db_utils_parkingLots import (
    load_parking_lots,
    load_parking_lot_by_id,
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
    d = lot.__dict__

    capacity = int(d.get("capacity", 0) or 0)
    active = int(d.get("active_sessions", 0) or 0)
    reserved = int(d.get("reserved", 0) or 0)

    spaces_left = max(capacity - active - reserved, 0)

    return {
        "name": d.get("name"),
        "location": d.get("location"),
        "address": d.get("address"),
        "spaces_left": spaces_left,
        "tariff": d.get("tariff"),
        "daytariff": d.get("daytariff"),
    }


def do_GET(self):
    parts = self.path.strip("/").split("/")

    session_user = require_session(self)
    if not session_user:
        return
    if parts[0] == "parking-lots" and len(parts) > 1 and parts[1] == "sessions":
        return parkingSessions.do_GET(self)

    if parts[0] == "parking-lots":
        is_admin = session_user.get("role") == "ADMIN"

        if len(parts) == 1:
            lots = load_parking_lots()
            if is_admin:
                return send_json(self, 200, {lot_id: lot.__dict__ for lot_id, lot in lots.items()})
            else:
                return send_json(self, 200, {lot_id: lot_to_public_dict(lot) for lot_id, lot in lots.items()})

        if len(parts) == 2:
            lot = load_parking_lot_by_id(parts[1])
            if lot:
                if is_admin:
                    return send_json(self, 200, lot.__dict__)
                else:
                    return send_json(self, 200, lot_to_public_dict(lot))
            else:
                return send_json(self, 404, {"error": "Not found"})

    return send_json(self, 404, {"error": "Invalid route"})


def do_POST(self):
    parts = self.path.strip("/").split("/")

    session_user = require_session(self)
    if not session_user:
        return

    if len(parts) == 1 and parts[0] == "parking-lots":
        if not require_admin(self, session_user):
            return

        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))
        new_id = save_parking_lot(data)
        return send_json(self, 201, {"id": new_id})
    if len(parts) > 1 and parts[0] == "parking-lots" and parts[1] == "sessions":
        return parkingSessions.do_POST(self)

    return send_json(self, 404, {"error": "Invalid route"})


def do_PUT(self):
    parts = self.path.strip("/").split("/")


    session_user = require_session(self)
    if not session_user:
        return

    if len(parts) == 2 and parts[0] == "parking-lots":
        if not require_admin(self, session_user):
            return

        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))
        update_parking_lot(parts[1], data)
        return send_json(self, 200, {"message": "Updated"})

    return send_json(self, 404, {"error": "Invalid route"})


def do_DELETE(self):
    parts = self.path.strip("/").split("/")

    session_user = require_session(self)
    if not session_user:
        return

    if len(parts) == 2 and parts[0] == "parking-lots":
        if not require_admin(self, session_user):
            return

        lot = load_parking_lot_by_id(parts[1])
        if not lot:
            return send_json(self, 404, {"error": "Parking lot does not exist"})
        delete_parking_lot(parts[1])
        return send_json(self, 200, {"message": "Deleted"})

    return send_json(self, 404, {"error": "Invalid route"})
