import json
import hashlib
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from MobyPark.db.users import User, UserRole
from storage_utils import load_json, save_data, save_user_data, load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import add_session, remove_session, get_session # pyright: ignore[reportUnknownVariableType]
import session_calculator as sc


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):

        if self.path == "/register":
            from handlers.user import do_POST as handle_post
            handle_post(self)
            return

        elif self.path == "/login":
            from handlers.user import do_POST as handle_post
            handle_post(self)
            return

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
            from handlers.user import do_PUT as handle_put
            handle_put(self)
            return

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
            from handlers.user import do_GET as handle_get
            handle_get(self)
            return

        elif self.path == "/logout":
            from handlers.user import do_GET as handle_get
            handle_get(self)
            return

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
                token = self.headers.get('Authorization')
                session_user = get_session(token)
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
                users = User.get_all_users()
                user = session_user.username

                user_vehicles = [
                    v for v in vehicles
                    if v.get("user_id") == session_user.id
                ]

                if session_user.role == UserRole.ADMIN and self.path != "/vehicles":
                    user = self.path.replace("/vehicles/", "")
                    if user not in [u.username for u in users]:
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
