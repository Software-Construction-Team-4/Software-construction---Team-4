import json
from datetime import datetime
from storage_utils import load_payment_data, save_payment_data
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
