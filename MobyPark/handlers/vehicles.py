import json
from datetime import datetime
from storage_utils import load_json, save_data, save_user_data, load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session
import session_calculator as sc

def do_POST(self):
    if self.path == "/vehicles":
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

            uvehicles = {
                v["id"]: v
                for v in vehicles
                if v.get("user_id") == session_user.get("user_id")
            }
            for field in ["name", "license_plate"]:
                if not field in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return
            lid = data["license_plate"].replace("-", "")
            if lid in uvehicles:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Vehicle already exists", "data": uvehicles.get(lid)}).encode("utf-8"))
                return
            if not uvehicles:
                vehicles[session_user["username"]] = {}
            vehicles[session_user["username"]][lid] = {
                "licenseplate": data["license_plate"],
                "name": data["name"],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            save_data("data/vehicles.json", vehicles)
            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Success", "vehicle": data}).encode("utf-8"))
            return

    elif self.path.startswith("/vehicles/"):
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

            uvehicles = {
                v["id"]: v
                for v in vehicles
                if v.get("user_id") == session_user.get("user_id")
            }

            for field in ["parkinglot"]:
                if not field in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return
            lid = self.path.replace("/vehicles/", "").replace("/entry", "")
            if lid not in uvehicles:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Vehicle does not exist", "data": lid}).encode("utf-8"))
                return
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Accepted", "vehicle": vehicles[session_user["username"]][lid]}).encode("utf-8"))
            return

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
            checkIdVehicle = next((v for v in vehicles if v.get("id") == lid), None)

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
            checkIdVehicle["updated at"] = datetime.now().strftime("%Y-%m-%d")

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
                if v.get("user_id") == session_user.get("user_id")
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
