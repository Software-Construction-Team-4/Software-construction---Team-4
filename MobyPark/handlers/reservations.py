import json
from datetime import datetime, date
from DataAccesLayer.db_utils_reservations import save_reservation_data, load_reservation_data, update_reservation_data, delete_reservation  # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session
from DataModels.reservationsModel import Reservations
from DataAccesLayer.vehicle_access import VehicleAccess
from DataAccesLayer.db_utils_parkingLots import save_parking_lot, load_parking_lots, update_parking_lot

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

        id_of_user = session_user.get("user_id")

        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        parking_lots = load_parking_lots()

        for field in ["start_time", "end_time", "status", "cost", "parking_lot_id"]:
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
        
        if not VehicleAccess.get_all_user_vehicles(id_of_user):
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "User is not registerd to any vehicle"}).encode("utf-8"))
            return

        parking_lot = parking_lots[data["parking_lot_id"]]["reserved"] + 1

        user_vehicles = VehicleAccess.get_all_user_vehicles(id_of_user)

        new_reservation = Reservations(
            id=None,
            user_id=id_of_user,
            parking_lot_id=data["parking_lot_id"],
            vehicle_id=user_vehicles[0].id,
            start_time=data["start_time"],
            end_time=data["end_time"],
            status=data["status"],
            created_at=data.get("created_at", date.today()),
            cost=data["cost"],
            updated_at=None
        )

        save_reservation_data(new_reservation)
        update_parking_lot(parking_lot["id"], parking_lot)

        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {"status": "Success", "reservation": new_reservation.to_dict()},
                default=str
            ).encode("utf-8")
        )

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

        for field in ["parking_lot_id", "start_time", "end_time", "status", "created_at", "cost", "updated_at"]:
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
        
        user_vehicles = VehicleAccess.get_all_user_vehicles(session_user.get("user_id"))

        updated_reservation = Reservations(
            id=found_res_dict["id"],
            user_id=session_user.get("user_id"),
            parking_lot_id=data["parking_lot_id"],
            vehicle_id=user_vehicles[0].id,
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
    # this shouldnt delete a reservation but keep it and update the status to cancelled
    # cancelation must be 24 hours before the starts_time
    if self.path.startswith("/reservations/"):
        reservations_data = load_reservation_data()
        parking_lots = load_parking_lots()
        rid = self.path.replace("/reservations/", "").strip("/")

        if rid:
            found_res_dict = next((r for r in reservations_data if str(r.get("id")) == str(rid)), None)

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

            now = datetime.now()
            difference = reservation.start_time - now
            hours_left = difference.total_seconds() / 3600
            
            if hours_left < 24:
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                message = {
                    "error": "Can't cancel less than 24 hours before the start time of the reservation"
                }
                self.wfile.write(json.dumps(message).encode("utf-8"))
                return


            pid = reservation.parking_lot_id
            if pid in parking_lots:
                parking_lots[pid]["reserved"] -= 1

            # delete_reservation(reservation)

            reservation.status = "canceled"

            update_reservation_data(reservation)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Canceled"}).encode("utf-8"))
            return

