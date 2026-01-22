import json
from DataAccesLayer.vehicle_access import VehicleAccess
from DataModels.vehicle_model import VehicleModel
from session_manager import get_session


def do_POST(self):

    if self.path == "/vehicles":
        token = self.headers.get("Authorization")
        session = get_session(token) if token else None

        if not token or not session:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Unauthorized",
                "message": "Invalid or missing session token"
            }).encode("utf-8"))
            return

        user_id = session["user_id"]

        content_length = int(self.headers.get("Content-Length", -1))
        raw_body = self.rfile.read(content_length)
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Invalid JSON body"
            }).encode("utf-8"))
            return
        required_fields = ["license_plate", "make", "model", "color", "year"]
        missing_fields = [f for f in required_fields if f not in data or data[f] in ("", None)]

        if missing_fields:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Missing required fields",
                "fields": missing_fields,
            }).encode("utf-8"))
            return

        if VehicleAccess.user_has_vehicle(user_id):
            self.send_response(409)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "User already has a vehicle"
            }).encode("utf-8"))
            return

        if VehicleAccess.license_plate_exists(data["license_plate"]):
            self.send_response(409)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "License plate alreaddy exists"
            }).encode("utf-8"))
            return

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

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "Success",
            "vehicle": created_vehicle.to_json()
        }).encode("utf-8"))


def do_PUT(self):

    if self.path.startswith("/vehicles/"):
        token = self.headers.get("Authorization")
        session = get_session(token) if token else None

        if not token or not session:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        content_length = int(self.headers.get("Content-Length", -1))
        data = json.loads(self.rfile.read(content_length))

        vid_str = self.path.replace("/vehicles/", "")
        try:
            vid = int(vid_str)
        except ValueError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Bad request: invalid vehicle id")
            return

        vehicle = VehicleAccess.get_by_id(vid)

        if vehicle is None:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Vehicle not found")
            return

        if vehicle.user_id != session["user_id"] and session["role"] != "ADMIN":
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Forbidden: cannot update this vehicle")
            return

        required_fields = ["license_plate", "make", "model", "color", "year"]
        for field in required_fields:
            if field not in data:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Required field missing",
                    "field": field
                }).encode("utf-8"))
                return

        vehicle.license_plate = data["license_plate"]
        vehicle.make = data["make"]
        vehicle.model = data["model"]
        vehicle.color = data["color"]
        vehicle.year = int(data["year"])

        updated_vehicle = VehicleAccess.update(vehicle)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "Updated",
            "vehicle": updated_vehicle.to_json()
        }).encode("utf-8"))


def do_GET(self):
    if self.path.startswith("/vehicles"):
        token = self.headers.get("Authorization")
        session = get_session(token) if token else None

        if not token or not session:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        user_id = session["user_id"]
        role = session["role"]

        if self.path == "/vehicles":
            if role == "ADMIN":
                vehicles = VehicleAccess.get_all_vehicles()
            else:
                vehicles = VehicleAccess.get_all_user_vehicles(user_id)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(
                [v.to_json() for v in vehicles],
                default=str
            ).encode("utf-8"))
            return

        if self.path.endswith("/reservations"):
            parts = self.path.split("/")
            try:
                vid = int(parts[2])
            except (IndexError, ValueError):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"Bad request: invalid vehicle id")
                return

            vehicle = VehicleAccess.get_by_id(vid)

            if vehicle is None:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"Not found!")
                return

            if vehicle.user_id != get_session(token)["user_id"] and get_session(token)["role"] != "ADMIN":
                self.send_response(403)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"Forbidden")
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(vehicle.to_json(), default=str).encode("utf-8"))
            return

        if self.path.startswith("/vehicles/"):
            vid_str = self.path.replace("/vehicles/", "")
            try:
                vid = int(vid_str)
            except ValueError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"Bad request: invalid vehicle id")
                return

            vehicle = VehicleAccess.get_by_id(vid)

            if vehicle is None:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"Vehicle not found")
                return

            if vehicle.user_id != get_session(token)["user_id"] and get_session(token)["role"] != "ADMIN":
                self.send_response(403)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"Forbidden")
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(vehicle.to_json(), default=str).encode("utf-8"))
            return


def do_DELETE(self):

    if self.path.startswith("/vehicles/"):
        token = self.headers.get("Authorization")
        session = get_session(token) if token else None

        if not token or not session:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        if session["role"] != "ADMIN":
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Forbidden: only admins can delete vehicles")
            return

        vid_str = self.path.replace("/vehicles/", "")
        try:
            vid = int(vid_str)
        except ValueError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Bad request: invalid vehicle id")
            return

        vehicle = VehicleAccess.get_by_id(vid)

        if vehicle is None:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Vehicle not found!")
            return

        VehicleAccess.delete(vehicle)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Deleted"}).encode("utf-8"))
        return
    

#test
