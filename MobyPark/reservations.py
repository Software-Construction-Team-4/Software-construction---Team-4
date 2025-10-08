import json
from datetime import datetime
from storage_utils import load_json, save_data, save_user_data, load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session
import session_calculator as sc

def do_POST(self):
    if self.path == "/reservations":
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

def do_PUT(self):
    if self.path.startswith("/reservations/"):
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


def do_GET(self):
    if self.path.startswith("/reservations/"):
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


def do_DELETE(self):
    if self.path.startswith("/reservations/"):
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
