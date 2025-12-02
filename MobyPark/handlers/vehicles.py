import json
from DataAccesLayer.vehicle_access import VehicleAccess
from DataModels.vehicle_model import VehicleModel
from session_manager import get_session


def do_POST(self):
    """
    Create a vehicle for the logged-in user.
    Users & admins can both create, but a user can only have one vehicle.
    """
    if self.path == "/vehicles":
        token = self.headers.get("Authorization")
        session = get_session(token) if token else None

        if not token or not session:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        user_id = session["user_id"]

        content_length = int(self.headers.get("Content-Length", -1))
        data = json.loads(self.rfile.read(content_length))

        required_fields = ["license_plate", "make", "model", "color", "year"]
        missing_fields = [f for f in required_fields if f not in data or not data[f]]

        if missing_fields:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Missing required fields",
                "fields": missing_fields,
            }).encode("utf-8"))
            return

        # Only one vehicle per user
        if VehicleAccess.user_has_vehicle(user_id):
            self.send_response(409)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "User already has a vehicle"
            }).encode("utf-8"))
            return

        vehicle = VehicleModel(
            -1,
            user_id,
            data["license_plate"],
            data["make"],
            data["model"],
            data["color"],
            int(data["year"])
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
    """
    Update a vehicle.
    ONLY admins are allowed to update, for ANY car.
    Normal users always get 403.
    """
    if self.path.startswith("/vehicles/"):
        token = self.headers.get("Authorization")
        session = get_session(token) if token else None

        if not token or not session:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        # Only admins can update vehicles
        if session["role"] != "ADMIN":
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Forbidden: only admins can update vehicles")
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

        # Validate required fields
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

        # Apply update
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
    """
    Get vehicles or specific vehicle info.
    - GET /vehicles          -> admin: all vehicles, user: own vehicles
    - GET /vehicles/<id>     -> admin: any vehicle, user: only own
    - GET /vehicles/<id>/reservations -> example guarded with your admin check pattern
    """
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

        # /vehicles
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

        # /vehicles/<id>/reservations (example, uses your admin-check style)
        if self.path.endswith("/reservations"):
            parts = self.path.split("/")
            # expected: ['', 'vehicles', '<id>', 'reservations']
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

            # YOUR STYLE:
            # if foundUser.id != get_session(token)['user_id'] and get_session(token)['role'] != "ADMIN":
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

        # /vehicles/<id>
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

            # Use your admin check style here as well:
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
    """
    Delete a vehicle.
    ONLY admins can delete any vehicle.
    Normal users always get 403.
    """
    if self.path.startswith("/vehicles/"):
        token = self.headers.get("Authorization")
        session = get_session(token) if token else None

        if not token or not session:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        # Only admins may delete vehicles
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
