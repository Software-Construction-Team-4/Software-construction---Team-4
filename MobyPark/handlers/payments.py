import json
from datetime import datetime
from storage_utils import load_json, save_data, save_user_data, load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session
import session_calculator as sc


# class RequestHandler(BaseHTTPRequestHandler):
def do_POST(self):
    if self.path.startswith("/payments"):
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        payments = load_payment_data()
        session_user = get_session(token)
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        if self.path.endswith("/refund"):
            if session_user.get('role') != 'ADMIN':
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Access denied")
                return

            for field in ["amount"]:
                if field not in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return

            payment = {
                "transaction": data["transaction"] if data.get("transaction") else sc.generate_payment_hash(
                    session_user["username"], str(datetime.now())
                ),
                "amount": -abs(data.get("amount", 0)),
                "coupled_to": data.get("coupled_to"),
                "processed_by": session_user["username"],
                "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "completed": False,
                "hash": sc.generate_transaction_validation_hash()
            }
        else:
            for field in ["transaction", "amount"]:
                if field not in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return

            payment = {
                "transaction": data.get("transaction"),
                "amount": data.get("amount", 0),
                "initiator": session_user["username"],
                "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "completed": False,
                "hash": sc.generate_transaction_validation_hash()
            }

        payments.append(payment)
        save_payment_data(payments)
        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Success", "payment": payment}).encode("utf-8"))
        return

def do_PUT(self):
    if self.path.startswith("/payments/"):
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        pid = self.path.replace("/payments/", "")
        payments = load_payment_data()
        session_user = get_session(token)
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        payment = next((p for p in payments if p["transaction"] == pid), None)
        if payment:
            for field in ["t_data", "validation"]:
                if field not in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return

            if payment["hash"] != data.get("validation"):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Validation failed",
                    "info": "The validation of the security hash could not be validated for this transaction."
                }).encode("utf-8"))
                return

            payment["completed"] = True
            payment["completed_at"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            payment["t_data"] = data.get("t_data", {})
            save_payment_data(payments)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Success", "payment": payment}, default=str).encode("utf-8"))
            return
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Payment not found!")
            return


def do_GET(self):
    if self.path == "/payments":
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        payments = []
        session_user = get_session(token)
        for payment in load_payment_data():
            if payment.get("initiator") == session_user["username"]:
                payments.append(payment)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payments).encode("utf-8"))
        return

    elif self.path.startswith("/payments/"):
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        session_user = get_session(token)
        user = self.path.replace("/payments/", "").strip("/")

        if session_user.get('role') != "ADMIN":
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Access denied")
            return

        payments = []
        for payment in load_payment_data():
            if payment.get("initiator") == user:
                payments.append(payment)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payments).encode("utf-8"))
        return

    elif self.path == "/billing":
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        data = []
        session_user = get_session(token)
        parking_data = load_parking_lot_data()
        for pid, parkinglot in parking_data.items():
            sessions = load_json(f'data/pdata/p{pid}-sessions.json', default={})
            for sid, session in sessions.items():
                if session.get("user") == session_user["username"]:
                    amount, hours, days = sc.calculate_price(parkinglot, sid, session)
                    transaction = sc.generate_payment_hash(sid, session)
                    payed = sc.check_payment_amount(transaction)
                    data.append({
                        "session": {k: v for k, v in session.items() if k in ["licenseplate", "started", "stopped"]} | {"hours": hours, "days": days},
                        "parking": {k: v for k, v in parkinglot.items() if k in ["name", "location", "tariff", "daytariff"]},
                        "amount": amount,
                        "thash": transaction,
                        "payed": payed,
                        "balance": amount - payed
                    })

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))
        return


def do_GET_test(self):
    if self.path.startswith("/billing/"):
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        session_user = get_session(token)
        if session_user.get('role') != "ADMIN":
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Access denied")
            return

        user = self.path.replace("/billing/", "")
        data = []
        parking_data = load_parking_lot_data()
        for pid, parkinglot in parking_data.items():
            sessions = load_json(f'data/pdata/p{pid}-sessions.json', default={})
            for sid, session in sessions.items():
                if session.get("user") == user:
                    amount, hours, days = sc.calculate_price(parkinglot, sid, session)
                    transaction = sc.generate_payment_hash(sid, session)
                    payed = sc.check_payment_amount(transaction)
                    data.append({
                        "session": {k: v for k, v in session.items() if k in ["licenseplate", "started", "stopped"]} | {"hours": hours, "days": days},
                        "parking": {k: v for k, v in parkinglot.items() if k in ["name", "location", "tariff", "daytariff"]},
                        "amount": amount,
                        "thash": transaction,
                        "payed": payed,
                        "balance": amount - payed
                    })

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))
        return
