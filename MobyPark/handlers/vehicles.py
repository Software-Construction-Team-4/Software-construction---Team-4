import json
from datetime import datetime
from db_utils_vehicles import load_json, save_data# pyright: ignore[reportUnknownVariableType]
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
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
        vehicles = load_json("data/vehicles.json")

        required_fields = ["license_plate", "make", "model", "color", "year"]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Missing required fields", "fields": missing_fields}).encode("utf-8")
            )
            return

        # Check if vehicle already exists for this user
        uvehicles = {v["license_plate"].replace("-", ""): v for v in vehicles if v["user_id"] == session_user["id"]}
        lid = data["license_plate"].replace("-", "")
        if lid in uvehicles:
            self.send_response(409)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Vehicle already exists", "vehicle": uvehicles[lid]}).encode("utf-8")
            )
            return


        new_vehicle = {
            "id": max([v["id"] for v in vehicles] + [0]) + 1,
            "user_id": session_user["id"],
            "license_plate": data["license_plate"],
            "make": data["make"],
            "model": data["model"],
            "color": data["color"],
            "year": int(data["year"]),
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "updated_at": datetime.now().strftime("%Y-%m-%d")
        }

        vehicles.append(new_vehicle)
        save_data("data/vehicles.json", vehicles)

        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Success", "vehicle": new_vehicle}).encode("utf-8"))

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
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            vehicles = load_json("data/vehicles.json")
            lid = self.path.replace("/vehicles/", "")
            checkIdVehicle = next((v for v in vehicles if v.get("id") == int(lid)), None)

            if checkIdVehicle is None:
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

            checkIdVehicle["license_plate"] = data["license_plate"]
            checkIdVehicle["make"] = data["make"]
            checkIdVehicle["model"] = data["model"]
            checkIdVehicle["color"] = data["color"]
            checkIdVehicle["year"] = data["year"]
            checkIdVehicle["updated_at"] = datetime.now().strftime("%Y-%m-%d")

            save_data("data/vehicles.json", vehicles)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Updated", "vehicle": checkIdVehicle}, default=str).encode("utf-8"))
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
                vid = self.path.split("/")[2]
                vehicles = load_json("data/vehicles.json")

                uvehicles = {
                v["id"]: v
                for v in vehicles
                if v.get("user_id") == session_user.get("id")
            }
                if vid not in uvehicles:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Not found!")
                    return
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps([]).encode("utf-8"))
                return


def do_DELETE(self):
    if self.path.startswith("/vehicles/"):
            lid = self.path.replace("/vehicles/", "")
            if lid:
                token = self.headers.get('Authorization')
                if not token or not get_session(token):
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Unauthorized: Invalid or missing session token")
                    return

                session_user = get_session(token)
                vehicles = load_json("data/vehicles.json")

                uvehicles = {v["id"]: v for v in vehicles if v.get("user_id") == session_user.get("id")}

                if lid not in uvehicles:
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Vehicle not found!")
                    return

                vehicles = [v for v in vehicles if v["id"] != lid]

                save_data("data/vehicles.json", vehicles)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "Deleted"}).encode("utf-8"))
                return
