import json
from datetime import datetime, date
from DataAccesLayer.db_utils_reservations import load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, update_reservation_data, delete_reservation  # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session
from DataModels.reservationsModel import Reservations

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

        for field in ["licenseplate", "parking_lot_id"]:
            if field not in data:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Required field missing", "field": field}).encode("utf-8"))
                return

        if data.get("parking_lot_id") not in parking_lots:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Parking lot not found", "field": "parking_lot_id"}).encode("utf-8"))
            return

        if session_user.get("role") == "ADMIN":
            if "user_id" not in data:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Required field missing", "field": "user_id"}).encode("utf-8"))
                return
            user_id = data["user_id"]
        else:
            user_id = session_user["user_id"]

        parking_lots[data["parking_lot_id"]]["reserved"] += 1

        new_reservation = Reservations(
            id=None,
            user_id=user_id,
            parking_lot_id=data["parking_lot_id"],
            vehicle_id=data["vehicle_id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            status=data["status"],
            created_at=data.get("created_at", date.today()),
            cost=data["cost"],
            updated_at=None
        )

        save_reservation_data(new_reservation)
        save_parking_lot_data(parking_lots)

        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Success", "reservation": new_reservation.to_dict()}).encode("utf-8"))

def do_PUT(self):
    if self.path.startswith("/reservations/"):
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
        reservations = load_reservation_data()
        rid = self.path.replace("/reservations/", "")

        found_res_dict = next((r for r in reservations if str(r["id"]) == str(rid)), None)
        if found_res_dict is None:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Reservation not found")
            return

        token = self.headers.get('Authorization')
        session_user = get_session(token)
        if not token or not session_user:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        for field in ["user_id", "parking_lot_id", "vehicle_id", "start_time", "end_time", "status", "created_at", "cost", "updated_at"]:
            if field not in data:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Required field missing", "field": field}).encode("utf-8"))
                return

        if session_user.get('role') != 'ADMIN' and str(found_res_dict.get("user_id")) != str(session_user.get('user_id')):
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            message = {
                "error": "Access denied",
                "session_role": session_user.get("role"),
                "session_user_id": session_user.get('user_id'),
                "reservation_user_id": found_res_dict.get("user_id")
            }
            self.wfile.write(json.dumps(message).encode("utf-8"))
            return

        updated_reservation = Reservations(
            id=found_res_dict["id"],
            user_id=data.get("user_id", found_res_dict["user_id"]),
            parking_lot_id=data["parking_lot_id"],
            vehicle_id=data["vehicle_id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            status=data["status"],
            created_at=data.get("created_at", found_res_dict["created_at"]),
            cost=data["cost"],
            updated_at=datetime.now()
        )

        update_reservation_data(updated_reservation)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "Updated",
            "reservation": updated_reservation.to_dict()
        }, default=str).encode("utf-8"))


def do_GET(self):
    if self.path.startswith("/reservations/"):
        reservations_data = load_reservation_data()
        rid = self.path.replace("/reservations/", "").strip("/")

        if rid:
            found_res_dict = next((r for r in reservations_data if str(r["id"]) == str(rid)), None)

            if not found_res_dict:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Reservation not found")
                return

            reservation = Reservations(
                id=str(rid),
                user_id=found_res_dict["user_id"],
                parking_lot_id=found_res_dict["parking_lot_id"],
                vehicle_id=found_res_dict["vehicle_id"],
                start_time=found_res_dict["start_time"],
                end_time=found_res_dict["end_time"],
                status=found_res_dict["status"],
                created_at=found_res_dict["created_at"],
                cost=found_res_dict["cost"],
                updated_at=found_res_dict.get("updated_at")
            )

            token = self.headers.get('Authorization')
            session_user = get_session(token)
            if not token or not session_user:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return

            if session_user.get("role") != "ADMIN" and str(session_user.get('user_id')) != str(reservation.user_id):
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                message = {
                    "error": "Access denied",
                    "session_role": session_user.get("role"),
                    "session_user_id": session_user.get('user_id'),
                    "reservation_user_id": reservation.user_id
                }
                self.wfile.write(json.dumps(message).encode("utf-8"))
                return

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(reservation.to_dict(), default=str).encode("utf-8"))
            return


def do_DELETE(self):
    if self.path.startswith("/reservations/"):
        reservations_data = load_reservation_data()
        parking_lots = load_parking_lot_data()
        rid = self.path.replace("/reservations/", "").strip("/")

        if rid:
            found_res_dict = next((r for r in reservations_data if str(r.get("id")) == rid), None)

            if not found_res_dict:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Reservation not found")
                return

            reservation = Reservations(
                id=found_res_dict["id"],
                user_id=found_res_dict["user_id"],
                parking_lot_id=found_res_dict["parking_lot_id"],
                vehicle_id=found_res_dict["vehicle_id"],
                start_time=found_res_dict["start_time"],
                end_time=found_res_dict["end_time"],
                status=found_res_dict["status"],
                created_at=found_res_dict["created_at"],
                cost=found_res_dict["cost"],
                updated_at=found_res_dict.get("updated_at")
            )

            token = self.headers.get('Authorization')
            session_user = get_session(token)
            if not token or not session_user:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return

            if session_user.get("role") != "ADMIN" and str(session_user.get("user_id")) != str(reservation.user_id):
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                message = {
                    "error": "Access denied",
                    "session_role": session_user.get("role"),
                    "session_user_id": session_user.get('user_id'),
                    "reservation_user_id": reservation.user_id
                }
                self.wfile.write(json.dumps(message).encode("utf-8"))
                return

            pid = reservation.parking_lot_id
            if pid in parking_lots:
                parking_lots[pid]["reserved"] -= 1

            delete_reservation(reservation)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Deleted"}).encode("utf-8"))
            return

