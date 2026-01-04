# handlers/vehicles.py

import json
from mysql.connector import Error as MySQLError

from DataAccesLayer.vehicle_access import VehicleAccess, UserAlreadyHasVehicleError
from DataModels.vehicle_model import VehicleModel
from session_manager import get_session


def _send_json(self, status_code: int, payload: dict):
    self.send_response(status_code)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(payload).encode("utf-8"))


def do_POST(self):
    if self.path != "/vehicles":
        return

    token = self.headers.get("Authorization")
    session = get_session(token) if token else None

    if not token or not session:
        _send_json(self, 401, {
            "error": "Unauthorized",
            "message": "Invalid or missing session token"
        })
        return

    user_id = session["user_id"]

    content_length = int(self.headers.get("Content-Length", -1))
    raw_body = self.rfile.read(content_length)

    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        _send_json(self, 400, {"error": "Invalid JSON body"})
        return

    required_fields = ["license_plate", "make", "model", "color", "year"]
    missing_fields = [f for f in required_fields if f not in data or data[f] in ("", None)]
    if missing_fields:
        _send_json(self, 400, {
            "error": "Missing required fields",
            "fields": missing_fields
        })
        return

    try:
        vehicle = VehicleModel(
            -1,
            user_id,
            data["license_plate"],
            data["make"],
            data["model"],
            data["color"],
            int(data["year"]),
        )

        created_vehicle = VehicleAccess.create(vehicle)

        _send_json(self, 201, {
            "status": "Success",
            "vehicle": created_vehicle.to_json() if created_vehicle else None
        })

    except UserAlreadyHasVehicleError:
        _send_json(self, 409, {"error": "User already has a vehicle"})
        return

    except (MySQLError, Exception):
        # This prevents the HTTP connection from being closed without a response
        _send_json(self, 500, {"error": "Database error"})
        return


def do_PUT(self):
    if not self.path.startswith("/vehicles/"):
        return

    token = self.headers.get("Authorization")
    session = get_session(token) if token else None
    if not token or not session:
        _send_json(self, 401, {"error": "Unauthorized"})
        return

    content_length = int(self.headers.get("Content-Length", -1))
    try:
        data = json.loads(self.rfile.read(content_length))
    except json.JSONDecodeError:
        _send_json(self, 400, {"error": "Invalid JSON body"})
        return

    vid_str = self.path.replace("/vehicles/", "")
    try:
        vid = int(vid_str)
    except ValueError:
        _send_json(self, 400, {"error": "Bad request: invalid vehicle id"})
        return

    try:
        vehicle = VehicleAccess.get_by_id(vid)
        if vehicle is None:
            _send_json(self, 404, {"error": "Vehicle not found"})
            return

        if vehicle.user_id != session["user_id"] and session["role"] != "ADMIN":
            _send_json(self, 403, {"error": "Forbidden"})
            return

        required_fields = ["license_plate", "make", "model", "color", "year"]
        for field in required_fields:
            if field not in data:
                _send_json(self, 400, {"error": "Required field missing", "field": field})
                return

        vehicle.license_plate = data["license_plate"]
        vehicle.make = data["make"]
        vehicle.model = data["model"]
        vehicle.color = data["color"]
        vehicle.year = int(data["year"])

        updated_vehicle = VehicleAccess.update(vehicle)

        _send_json(self, 200, {
            "status": "Updated",
            "vehicle": updated_vehicle.to_json()
        })

    except (MySQLError, Exception):
        _send_json(self, 500, {"error": "Database error"})
        return


def do_GET(self):
    if not self.path.startswith("/vehicles"):
        return

    token = self.headers.get("Authorization")
    session = get_session(token) if token else None
    if not token or not session:
        _send_json(self, 401, {"error": "Unauthorized"})
        return

    user_id = session["user_id"]
    role = session["role"]

    try:
        if self.path == "/vehicles":
            vehicles = VehicleAccess.get_all_vehicles() if role == "ADMIN" else VehicleAccess.get_all_user_vehicles(user_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps([v.to_json() for v in vehicles], default=str).encode("utf-8"))
            return

        if self.path.startswith("/vehicles/"):
            vid_str = self.path.replace("/vehicles/", "").split("/")[0]
            try:
                vid = int(vid_str)
            except ValueError:
                _send_json(self, 400, {"error": "Bad request: invalid vehicle id"})
                return

            vehicle = VehicleAccess.get_by_id(vid)
            if vehicle is None:
                _send_json(self, 404, {"error": "Vehicle not found"})
                return

            if vehicle.user_id != session["user_id"] and session["role"] != "ADMIN":
                _send_json(self, 403, {"error": "Forbidden"})
                return

            _send_json(self, 200, vehicle.to_json())
            return

    except (MySQLError, Exception):
        _send_json(self, 500, {"error": "Database error"})
        return


def do_DELETE(self):
    if not self.path.startswith("/vehicles/"):
        return

    token = self.headers.get("Authorization")
    session = get_session(token) if token else None
    if not token or not session:
        _send_json(self, 401, {"error": "Unauthorized"})
        return

    if session["role"] != "ADMIN":
        _send_json(self, 403, {"error": "Forbidden: only admins can delete vehicles"})
        return

    vid_str = self.path.replace("/vehicles/", "")
    try:
        vid = int(vid_str)
    except ValueError:
        _send_json(self, 400, {"error": "Bad request: invalid vehicle id"})
        return

    try:
        vehicle = VehicleAccess.get_by_id(vid)
        if vehicle is None:
            _send_json(self, 404, {"error": "Vehicle not found"})
            return

        VehicleAccess.delete(vehicle)
        _send_json(self, 200, {"status": "Deleted"})
        return

    except (MySQLError, Exception):
        _send_json(self, 500, {"error": "Database error"})
        return
