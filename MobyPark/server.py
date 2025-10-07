import json
import hashlib
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from storage_utils import load_json, save_data, save_user_data, load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import add_session, remove_session, get_session # pyright: ignore[reportUnknownVariableType]
import session_calculator as sc
# from payments import do_POST as pay_POST, handle_put as do_PUT, handle_get as do_GET


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):

        if self.path == "/register":
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            username = data.get("username")
            password = data.get("password")
            name = data.get("name")
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            users = load_json('data/users.json')
            for user in users:
                if username == user['username']:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Username already taken")
                    return
            users.append({
                'username': username,
                'password': hashed_password,
                'name': name
            })
            save_user_data(users)
            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"User created")


        elif self.path == "/login":
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Missing credentials")
                return
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            users = load_json('data/users.json')
            for user in users:
                if user.get("username") == username:
                    if user.get("password") == hashed_password:
                        token = str(uuid.uuid4())
                        add_session(token, user)
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"message": "User logged in", "session_token": token}).encode('utf-8'))
                        return
                    else:
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Invalid credentials")
                        return
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"User not found")


        elif self.path.startswith("/parking-lots"):
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)
            if 'sessions' in self.path:
                lid = self.path.split("/")[2]
                data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
                sessions = load_json(f'data/pdata/p{lid}-sessions.json', default={})
                if self.path.endswith('start'):
                    if 'licenseplate' not in data:
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Require field missing", "field": 'licenseplate'}).encode("utf-8"))
                        return
                    filtered = {key: value for key, value in sessions.items() if value.get("licenseplate") == data['licenseplate'] and not value.get('stopped')}
                    if len(filtered) > 0:
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b'Cannot start a session when another sessions for this licesenplate is already started.')
                        return
                    session = {
                        "licenseplate": data['licenseplate'],
                        "started": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        "stopped": None,
                        "user": session_user["username"]
                    }
                    sessions[str(len(sessions) + 1)] = session
                    save_data(f'data/pdata/p{lid}-sessions.json', sessions)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(f"Session started for: {data['licenseplate']}".encode('utf-8'))

                elif self.path.endswith('stop'):
                    if 'licenseplate' not in data:
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Require field missing", "field": 'licenseplate'}).encode("utf-8"))
                        return
                    filtered = {key: value for key, value in sessions.items() if value.get("licenseplate") == data['licenseplate'] and not value.get('stopped')}
                    if len(filtered) < 0:
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b'Cannot stop a session when there is no session for this licesenplate.')
                        return
                    sid = next(iter(filtered))
                    sessions[sid]["stopped"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    save_data(f'data/pdata/p{lid}-sessions.json', sessions)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(f"Session stopped for: {data['licenseplate']}".encode('utf-8'))

            else:
                if not 'ADMIN' == session_user.get('role'):
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Access denied")
                    return
                data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
                parking_lots = load_parking_lot_data()
                new_lid = str(len(parking_lots) + 1)
                parking_lots[new_lid] = data
                save_parking_lot_data(parking_lots)
                self.send_response(201)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(f"Parking lot saved under ID: {new_lid}".encode('utf-8'))


        elif self.path == "/reservations":
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            reservations = load_reservation_data()
            parking_lots = load_parking_lot_data()

            rid = int(len(reservations) + 1)

            for field in ["licenseplate", "startdate", "enddate", "parkinglot"]:
                if not field in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return
            if data.get("parkinglot", -1) not in parking_lots:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Parking lot not found", "field": "parkinglot"}).encode("utf-8"))
                return
            if 'ADMIN' == session_user.get('role'):
                if not "user" in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": "user"}).encode("utf-8"))
                    return
            else:
                data["user"] = session_user["username"]
            reservations.append(data)
            rid = len(reservations)
            data["id"] = rid
            parking_lots[data["parkinglot"]]["reserved"] += 1
            save_reservation_data(reservations)
            save_parking_lot_data(parking_lots)
            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Success", "reservation": data}).encode("utf-8"))
            return

        elif self.path == "/vehicles":
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
        

        elif self.path.startswith("/payments"):
            from payments import do_POST as handle_post
            handle_post(self)
            return

    def do_PUT(self):
        if self.path.startswith("/parking-lots/"):
            lid = self.path.split("/")[2]
            parking_lots = load_parking_lot_data()
            if lid:
                if lid in parking_lots:
                    token = self.headers.get('Authorization')
                    if not token or not get_session(token):
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Unauthorized: Invalid or missing session token")
                        return
                    session_user = get_session(token)
                    if not 'ADMIN' == session_user.get('role'):
                        self.send_response(403)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Access denied")
                        return
                    data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
                    parking_lots[lid] = data
                    save_parking_lot_data(parking_lots)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Parking lot modified")
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Parking lot not found")
                    return


        elif self.path == "/profile":
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            users = load_json('data/users.json')

            data["username"] = session_user["username"]
            if data["password"]:
                data["password"] = hashlib.md5(data["password"].encode()).hexdigest()
            
            data["id"] = session_user["id"]

            for user in users:
                if session_user["username"] == user["username"] and session_user["password"] == user["password"]:
                    for key in data:
                        user[key] = data[key]

            save_user_data(users)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"User updated succesfully")


        elif self.path.startswith("/reservations/"):
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            reservations = load_reservation_data()
            rid = self.path.replace("/reservations/", "")

            foundRes = next((r for r in reservations if r["id"] == rid), None)

            if foundRes is None:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Reservation not found")
                return
                        
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)
            for field in ["start_time", "end_time", "parking_lot_id", "status", "vehicle_id", "cost"]:
                if not field in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return
            if 'ADMIN' == session_user.get('role'):
                if not "user_id" in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": "user_id"}).encode("utf-8"))
                    return
            else:
                data["user_id"] = session_user["id"]

            foundRes["user_id"] = data["user_id"]
            foundRes["parking_lot_id"] = data["parking_lot_id"]
            foundRes["vehicle_id"] = data["vehicle_id"]
            foundRes["start_time"] = data["start_time"]
            foundRes["end_time"] = data["end_time"]
            foundRes["status"] = data["status"]
            foundRes["cost"] = data["cost"]
            foundRes["updated_at"] = datetime.now().strftime("%Y-%m-%d")

            save_reservation_data(reservations)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            self.wfile.write(json.dumps({"status": "Updated", "reservation": foundRes}, default=str).encode("utf-8"))
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
        
    
        elif self.path.startswith("/payments/"):
            from payments import do_PUT as handle_put
            handle_put(self)
            return


    def do_DELETE(self):
        if self.path.startswith("/parking-lots/"):
            lid = self.path.split("/")[2]
            parking_lots = load_parking_lot_data()
            if lid:
                if lid in parking_lots:
                    token = self.headers.get('Authorization')
                    if not token or not get_session(token):
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Unauthorized: Invalid or missing session token")
                        return
                    session_user = get_session(token)
                    if not 'ADMIN' == session_user.get('role'):
                        self.send_response(403)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Access denied")
                        return
                    if 'sessions' in self.path:
                        sessions = load_json(f'data/pdata/p{lid}-sessions.json', default={})
                        sid = self.path.split("/")[-1]
                        if sid.isnumeric():
                            del sessions[sid]
                            save_data(f'data/pdata/p{lid}-sessions.json', sessions)
                            self.send_response(200)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(b"Sessions deleted")
                        else:
                            self.send_response(403)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(b"Session ID is required, cannot delete all sessions")
                    else:
                        del parking_lots[lid]
                        save_parking_lot_data(parking_lots)
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Parking lot deleted")
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Parking lot not found")
                    return


        elif self.path.startswith("/reservations/"):
            reservations = load_reservation_data()
            parking_lots = load_parking_lot_data()
            rid = self.path.replace("/reservations/", "")
            
            if rid:
                reservation = next((r for r in reservations if r.get("id") == rid), None)
                
                if reservation:
                    token = self.headers.get('Authorization')
                    if not token or not get_session(token):
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Unauthorized: Invalid or missing session token")
                        return
                    
                    session_user = get_session(token)
                    if session_user.get("role") == "ADMIN" or session_user["username"] == reservation.get("user_id"):
                        pid = reservation.get("parking_lot_id")
                        if pid in parking_lots:
                            parking_lots[pid]["reserved"] -= 1

                        reservations = [r for r in reservations if r.get("id") != rid]

                        save_reservation_data(reservations)
                        save_parking_lot_data(parking_lots)

                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "Deleted"}).encode("utf-8"))
                        return
                    else:
                        self.send_response(403)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Access denied")
                        return
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Reservation not found")
                    return

        elif self.path.startswith("/vehicles/"):
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

    def do_GET(self):
        if self.path == "/profile":
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(session_user).encode('utf-8'))


        elif self.path == "/logout":
            token = self.headers.get('Authorization')
            if token and get_session(token):
                remove_session(token)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"User logged out")
                return
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Invalid session token")


        elif self.path.startswith("/parking-lots/"):
            lid = self.path.split("/")[2]
            parking_lots = load_parking_lot_data()
            token = self.headers.get('Authorization')
            if lid:
                if lid not in parking_lots:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Parking lot not found")
                    return
                if 'sessions' in self.path:
                    if not token or not get_session(token):
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Unauthorized: Invalid or missing session token")
                        return
                    sessions = load_json(f'data/pdata/p{lid}-sessions.json', default={})
                    rsessions = []
                    if self.path.endswith('/sessions'):
                        if "ADMIN" == session_user.get('role'):
                            rsessions = sessions
                        else:
                            for session in sessions:
                                if session['user'] == session_user['username']:
                                    rsessions.append(session)
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(rsessions).encode('utf-8'))
                    else:
                        sid = self.path.split("/")[-1]
                        if not "ADMIN" == session_user.get('role') and not session_user["username"] == sessions[sid].get("user"):
                            self.send_response(403)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(b"Access denied")
                            return
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(sessions[sid]).encode('utf-8'))
                        return
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(parking_lots[lid]).encode('utf-8'))
                    return
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(parking_lots).encode('utf-8'))


        elif self.path.startswith("/reservations/"):
            reservations = load_reservation_data()
            rid = self.path.replace("/reservations/", "").strip("/")

            if rid:
                # find reservation in the list by ID
                reservation = next((r for r in reservations if str(r.get("id")) == rid), None)

                if reservation:
                    # authentication
                    token = self.headers.get('Authorization')
                    if not token or not get_session(token):
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Unauthorized: Invalid or missing session token")
                        return

                    session_user = get_session(token)

                    # authorization: admin or owner of reservation
                    if not (session_user.get('role') == "ADMIN" or session_user["username"] == reservation.get("user")):
                        self.send_response(403)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Access denied")
                        return

                    # return the reservation
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(reservation).encode("utf-8"))
                    return
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Reservation not found")
                    return
                
            
        elif self.path.startswith("/payments"):
            from payments import do_GET as handle_get
            handle_get(self)
            return
        

        elif self.path.startswith ("/billing/"):
            from payments import do_GET_test as handle_get1
            handle_get1(self)
            return
        
        elif self.path == "/billing":
            from payments import do_GET as handle_get
            handle_get(self)
            return

        elif self.path.startswith("/vehicles"):
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

            elif self.path.endswith("/history"):
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
            else:
                vehicles = load_json("data/vehicles.json")
                users = load_json('data/users.json')
                user = session_user["username"]

                user_vehicles = [
                    v for v in vehicles
                    if v.get("user_id") == session_user.get("user_id")
                ]

                if "ADMIN" == session_user.get("role") and self.path != "/vehicles":
                    user = self.path.replace("/vehicles/", "")
                    if user not in [u["username"] for u in users]:
                        self.send_response(404)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"User not found")
                        return
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(user_vehicles or [], default=str).encode("utf-8"))
                return
            
server = HTTPServer(('localhost', 8000), RequestHandler)
print("Server running on http://localhost:8000")
server.serve_forever()
