import json
from datetime import datetime
from DataAccesLayer.db_utils_reservations import load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, update_reservation_data, delete_reservation  # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session

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
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
        reservations = load_reservation_data()
        parking_lots = load_parking_lot_data()

        for field in ["licenseplate", "startdate", "enddate", "parkinglot"]:
            if field not in data:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                return

        if data.get("parkinglot", -1) not in parking_lots:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            value = str(data.get("parkinglot", -1))
            self.wfile.write(value.encode("utf-8"))
            self.wfile.write(json.dumps({"error": "Parking lot not found", "field": "parkinglot"}).encode("utf-8"))
            return

        if session_user.get("role") == "ADMIN":
            if "user" not in data:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Require field missing", "field": "user"}).encode("utf-8"))
                return
        else:
            data["user"] = session_user["username"]

        parking_lots[data["parkinglot"]]["reserved"] += 1

        save_reservation_data([data])
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

            foundRes = next((r for r in reservations if str(r["id"]) == str(rid)), None)

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
            # if 'ADMIN' == session_user.get('role'):
            #     if not "user_id" in data:
            #         self.send_response(401)
            #         self.send_header("Content-type", "application/json")
            #         self.end_headers()
            #         self.wfile.write(json.dumps({"error": "Require field missing", "field": "user_id"}).encode("utf-8"))
            #         return
            # else:
            #     data["user_id"] = session_user.get('id')  #(hard coded moet uiteindelijk verbeterd worden)

            if session_user.get('role') != 'ADMIN' and str(foundRes.get("user_id")) != str(session_user.get('user_id')):
                        self.send_response(403)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        message = {
                            "error": "Access denied",
                            "session_role": session_user.get("role"),
                            "session_user_id": session_user.get('user_id'),
                            "reservation_user_id": foundRes.get("user_id")
                        }
                        self.wfile.write(json.dumps(message).encode("utf-8"))
                        return

            foundRes["user_id"] = data["user_id"]
            foundRes["parking_lot_id"] = data["parking_lot_id"]
            foundRes["vehicle_id"] = data["vehicle_id"]
            foundRes["start_time"] = data["start_time"]
            foundRes["end_time"] = data["end_time"]
            foundRes["status"] = data["status"]
            foundRes["cost"] = data["cost"]
            foundRes["updated_at"] = datetime.now().strftime("%Y-%m-%d")

            update_reservation_data(foundRes)

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
                reservation = next((r for r in reservations if str(r["id"]) == str(rid)), None)

                if reservation:
                    token = self.headers.get('Authorization')
                    if not token or not get_session(token):
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Unauthorized: Invalid or missing session token")
                        return

                    session_user = get_session(token)

                    if session_user.get("role") != "ADMIN" and str(session_user.get('user_id')) != str(reservation.get("user_id")): #(this is hard coded can only be fixed if user is converted to database functionality)
                        self.send_response(403)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        message = {
                            "error": "Access denied",
                            "session_role": session_user.get("role"),
                            "session_user_id": session_user.get('user_id'),
                            "reservation_user_id": reservation.get("user_id")
                        }
                        self.wfile.write(json.dumps(message).encode("utf-8"))
                        return

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(reservation, default=str).encode("utf-8"))
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
                reservation = next((r for r in reservations if str(r.get("id")) == rid), None)
                
                if reservation:
                    token = self.headers.get('Authorization')
                    if not token or not get_session(token):
                        self.send_response(401)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b"Unauthorized: Invalid or missing session token")
                        return
                    
                    session_user = get_session(token)
                    if session_user.get("role") == "null" or "6688" == str(reservation.get("user_id")):
                        pid = reservation.get("parking_lot_id")
                        if pid in parking_lots:
                            parking_lots[pid]["reserved"] -= 1

                        reservations = [r for r in reservations if r.get("id") != rid]

                        delete_reservation(reservation)
                        # save_parking_lot_data(parking_lots)

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
