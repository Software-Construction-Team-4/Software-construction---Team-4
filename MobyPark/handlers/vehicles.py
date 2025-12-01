import json
from datetime import datetime
from DataAccesLayer.vehicle_access import VehicleAccess
from DataModels.vehicle_model import VehicleModel
from session_manager import get_session

def do_POST(self):
    if self.path == "/vehicles":
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        session_user = get_session(token)
        user_id = session_user["user_id"]

        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        required_fields = ["license_plate", "make", "model", "color", "year"]
        missing_fields = [f for f in required_fields if f not in data or not data[f]]

        if missing_fields:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Missing required fields",
                "fields": missing_fields
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
    if self.path.startswith("/vehicles/"):
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return

            session_user = get_session(token)
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

            lid = self.path.replace("/vehicles/", "")
            vehicle = VehicleAccess.get_by_id(int(lid))

            if (vehicle is None or vehicle.user_id != session_user["id"]):
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Vehicle not found")
                return

            for field in ["license_plate","make","model","color","year"]:
                if not field in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                return

            vehicle.license_plate = data["license_plate"]
            vehicle.make = data["make"]
            vehicle.model = data["model"]
            vehicle.color = data["color"]
            vehicle.year = data["year"]
            VehicleAccess.update(vehicle)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Updated", "vehicle": vehicle}, default=str).encode("utf-8"))
            return

def do_GET(self):
    if self.path.startswith("/vehicles"):
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)

            if self.path.endswith("/reservations"):
                vid = int(self.path.split("/")[2])
                vehicle = next((vehicle for vehicle in VehicleAccess.get_all_user_vehicles(session_user["id"]) if (vehicle.id == vid)), None)

                if vehicle is None:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Not found!")
                    return
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(vehicle, default=str).encode("utf-8"))
                return


def do_DELETE(self):
    if self.path.startswith("/vehicles/"):
            lid = int(self.path.replace("/vehicles/", ""))
            if lid:
                token = self.headers.get('Authorization')
                if not token or not get_session(token):
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Unauthorized: Invalid or missing session token")
                    return

                session_user = get_session(token)
                vehicle = next((vehicle for vehicle in VehicleAccess.get_all_user_vehicles(session_user["user_id"]) if (vehicle.id == lid)), None)

                if vehicle is None:
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Vehicle not found!")
                    return

                VehicleAccess.delete(vehicle)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "Deleted"}).encode("utf-8"))
                return
