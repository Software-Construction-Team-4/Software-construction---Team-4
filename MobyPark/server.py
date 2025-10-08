import json
import hashlib
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from storage_utils import load_json, save_data, save_user_data, load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import add_session, remove_session, get_session # pyright: ignore[reportUnknownVariableType]
import session_calculator as sc


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
            from handlers.parkingLots import do_POST as parking_post
            parking_post(self)
            return

        elif self.path == "/reservations":
            from handlers.reservations import do_POST as handle_post
            handle_post(self)
            return

        elif self.path == "/vehicles":
            from handlers.vehicles import do_POST as handle_post
            handle_post(self)
            return

        elif self.path.startswith("/vehicles/"):
            from handlers.vehicles import do_POST as handle_post
            handle_post(self)
            return
        

        elif self.path.startswith("/payments"):
            from handlers.payments import do_POST as handle_post
            handle_post(self)
            return

    def do_PUT(self):
        if self.path.startswith("/parking-lots/"):
            from handlers.parkingLots import do_PUT as parking_put
            parking_put(self)
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
            from handlers.reservations import do_PUT as handle_put
            handle_put(self)
            return


        elif self.path.startswith("/vehicles/"):
            from handlers.vehicles import do_PUT as handle_put
            handle_put(self)
            return
        
        elif self.path.startswith("/payments/"):
            from handlers.payments import do_PUT as handle_put
            handle_put(self)
            return


    def do_DELETE(self):
        if self.path.startswith("/parking-lots/"):
            from handlers.parkingLots import do_DELETE as parking_delete
            parking_delete(self)
            return


        elif self.path.startswith("/reservations/"):
            from handlers.reservations import do_DELETE as handle_delete
            handle_delete(self)
            return

        elif self.path.startswith("/vehicles/"):
            from handlers.vehicles import do_DELETE as handle_delete
            handle_delete(self)
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
            from handlers.parkingLots import do_GET as parking_get
            parking_get(self)
            return


        elif self.path.startswith("/reservations/"):
            from handlers.reservations import do_GET as handle_get
            handle_get(self)
            return
                
        elif self.path.startswith("/payments"):
            from handlers.payments import do_GET as handle_get
            handle_get(self)
            return
        

        elif self.path.startswith ("/billing/"):
            from handlers.payments import do_GET_test as handle_get1
            handle_get1(self)
            return
        
        elif self.path == "/billing":
            from handlers.payments import do_GET as handle_get
            handle_get(self)
            return

        elif self.path.startswith("/vehicles"):
            from handlers.vehicles import do_GET as handle_get
            handle_get(self)
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
