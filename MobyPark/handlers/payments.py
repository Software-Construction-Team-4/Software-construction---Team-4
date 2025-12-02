import json
from datetime import datetime
from storage_utils import load_json, load_parking_lot_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session
import session_calculator as sc
from DataAccesLayer.PaymentsAccess import PaymentsDataAccess, PaymentsModel
from DataAccesLayer.db_utils_parkingLots import load_parking_lots, load_parking_lot_by_id
from DataAccesLayer.db_utils_parkingSessions import load_sessions_by_userID

def do_POST(self):
    if self.path.startswith("/payments"):
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        #payments = load_payment_data()
        session_user = get_session(token)
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        if self.path.endswith("/refund"):
            if session_user.get('role') != 'ADMIN':
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Access denied")
                return

            for field in ["amount", "parking_lot_id"]:
                if field not in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return

            payment_hash = data.get("transaction") if data.get("transaction") else sc.generate_payment_hash()
            transaction_hash = sc.generate_transaction_validation_hash(data.get("session_id"), data.get("license_plate", ""))

            payment = PaymentsModel(
                amount=-abs(data.get("amount", 0)),
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                completed_at=None,
                payment_hash=payment_hash,
                initiator=session_user["username"],
                parking_lot_id=data["parking_lot_id"],
                session_id=data.get("session_id"),
                bank=None,
                transaction_date=None,
                issuer_code=None,
                payment_method=None,
                transaction_hash=transaction_hash
            )
        else:
            for field in ["parking_lot_id", "amount", "license_plate"]:
                if field not in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return

            # Resolve session_id: check if provided, otherwise lookup by license_plate in parking lot sessions
            session_id = data.get("session_id")
            if not session_id:
                sessions = load_json(f'data/pdata/p{data["parking_lot_id"]}-sessions.json', default={})
                for sid, session in sessions.items():
                    if session.get("licenseplate") == data["license_plate"]:
                        session_id = int(sid)
                        break

            payment_hash = data.get("transaction") if data.get("transaction") else sc.generate_payment_hash()
            transaction_hash = sc.generate_transaction_validation_hash(session_id, data["license_plate"])

            payment = PaymentsModel(
                amount=data["amount"],
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                completed_at=None,
                payment_hash=payment_hash,
                initiator=session_user["username"],
                parking_lot_id=data["parking_lot_id"],
                session_id=session_id,
                bank=data.get("bank"),
                transaction_date=data.get("transaction_date"),
                issuer_code=data.get("issuer_code"),
                payment_method=data.get("payment_method"),
                transaction_hash=transaction_hash
            )

        data_access = PaymentsDataAccess()
        payment_id = data_access.insert_payment(payment)
        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Success", "payment_id": payment_id}).encode("utf-8"))
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
        
        data_access = PaymentsDataAccess()
        pid = self.path.replace("/payments/", "")
        #payments = load_payment_data()
        session_user = get_session(token)
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        payment = data_access.get_by_id(pid)
        if payment:
            for field in ["payment_method", "bank", "issuer_code", "transaction_hash"]:
                if field not in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return

            if payment.transaction_hash != data.get("transaction_hash"):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Validation failed",
                    "info": "The validation of the security hash could not be validated for this transaction."
                }).encode("utf-8"))
                return

            payment.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payment.bank = data.get("bank")
            payment.transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payment.issuer_code = data.get("issuer_code")
            payment.payment_method = data.get("payment_method")
            data_access.update_payment(payment)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Success", "payment": payment.to_dict()}, default=str).encode("utf-8"))
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

        session_user = get_session(token)
        data_access = PaymentsDataAccess()
        payments = data_access.get_by_initiator(session_user["username"])
        #for payment in load_payment_data():
        #    if payment.get("initiator") == session_user["username"]:
        #        payments.append(payment)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payments, default=str).encode("utf-8"))
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

        data_access = PaymentsDataAccess()
        payments = data_access.get_by_initiator(user)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payments, default=str).encode("utf-8"))
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
        user = session_user.get("user_id")
        sessions = load_sessions_by_userID(user)
        data_access = PaymentsDataAccess()

        for sess in sessions:
            parkinglot_model = load_parking_lot_by_id(sess.parking_lot_id)
            if not parkinglot_model:
                continue

            parkinglot = {
                "tariff": float(parkinglot_model.tariff) if parkinglot_model.tariff else 0,
                "daytariff": float(parkinglot_model.daytariff) if parkinglot_model.daytariff else 0,
                "name": parkinglot_model.name,
                "location": parkinglot_model.location,
            }

            started = sess.started.strftime("%d-%m-%Y %H:%M:%S") if sess.started else None
            stopped = sess.stopped.strftime("%d-%m-%Y %H:%M:%S") if sess.stopped else None
            session_dict = {
                "licenseplate": sess.licenseplate,
                "started": started,
                "stopped": stopped,
                "user": sess.user_id
            }

            amount, hours, days = sc.calculate_price(parkinglot, str(sess.session), session_dict)

            transaction = sc.generate_transaction_validation_hash(sess.session, session_dict["licenseplate"])
            payed = sc.check_payment_amount(transaction)


            data.append({
                "session": {"licenseplate": session_dict["licenseplate"], "started": session_dict["started"], "stopped": session_dict["stopped"]} | {"hours": hours, "days": days},
                "parking": {"name": parkinglot["name"], "location": parkinglot["location"], "tariff": parkinglot["tariff"], "daytariff": parkinglot["daytariff"]},
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
                    transaction = sc.generate_transaction_validation_hash(sid, session.get("licenseplate"))
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
