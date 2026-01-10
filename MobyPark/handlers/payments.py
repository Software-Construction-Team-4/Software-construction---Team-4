import json
from datetime import datetime
#from storage_utils import load_json, load_parking_lot_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session
import session_calculator as sc
from DataAccesLayer.PaymentsAccess import PaymentsDataAccess, PaymentsModel
from DataAccesLayer.db_utils_parkingLots import load_parking_lot_by_id
from DataAccesLayer.db_utils_parkingSessions import load_sessions_by_userID, get_parking_session_for_payment, update_payment_status, update_payment_status_for_refund
from LogicLayer.paymentsLogic import create_issuer_code

def do_POST(self):
    if self.path.startswith("/payments"):
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        session_user = get_session(token)
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        if self.path.endswith("/refund"):
            if session_user.get('role') != 'ADMIN':
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Access denied")
                return

            if "id" not in data:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write("error: Require field missing, field: id".encode("utf-8"))
                return
            
            payments_instance = PaymentsDataAccess()
            payment = payments_instance.get_by_id(data.get("id"))
            update_payment_status_for_refund(payment.session_id)

            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write("succes: The user has been refunded".encode("utf-8"))
            return

        else:
            for field in ["bank", "payment_method"]:
                if field not in data:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Require field missing", "field": field}).encode("utf-8"))
                    return

            parking_session = get_parking_session_for_payment(session_user.get("user_id"))

            if parking_session == None:
                self.send_response(402)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write("You have no parking session that needs to be paid".encode("utf-8"))
                return

            payment_hash = sc.generate_payment_hash()
            transaction_hash = sc.generate_transaction_validation_hash(parking_session.session, parking_session.licenseplate)

            payment = PaymentsModel(
                amount=parking_session.cost,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                payment_hash=payment_hash,
                initiator=session_user.get("username"),
                parking_lot_id=parking_session.parking_lot_id,
                session_id=parking_session.id,
                bank=data.get("bank"),
                transaction_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                issuer_code=create_issuer_code(),
                payment_method=data.get("payment_method"),
                transaction_hash=transaction_hash
            )

        data_access = PaymentsDataAccess()
        payment_id = data_access.insert_payment(payment)
        update_payment_status(session_user.get("user_id"))
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
        
        session_user = get_session(token)
        if session_user.get('role') != 'ADMIN':
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Access denied")
            return
        
        data_access = PaymentsDataAccess()
        pid = self.path.replace("/payments/", "")
        # data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                data = {}
            else:
                raw_body = self.rfile.read(content_length)
                data = json.loads(raw_body.decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
            return

        payment = data_access.get_by_id(pid)
        if payment:
            if "transaction_hash" not in data:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Require field missing", "field": "transaction_hash"}).encode("utf-8"))
                return
        
            allowed_keys = ["payment_method", "bank", "issuer_code"]

            if not any(key in data for key in allowed_keys):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "you must give either 'bank', 'payment_method' or 'issuer_code' to update"}).encode("utf-8"))
                return

            if payment.transaction_hash != data.get("transaction_hash"):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Validation failed",
                    "info": "The validation of the security hash could not be validated for this transaction.",
                    "id": payment.id,
                    "transaction2": data.get("transaction_hash")
                }).encode("utf-8"))
                return

            for i in allowed_keys:
                if i in data:
                    setattr(payment, i, data[i])

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

        paymentsDict = [x.to_dict() for x in payments]
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(paymentsDict, default=str).encode("utf-8"))
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

        paymentsDict = [x.to_dict() for x in payments]
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(paymentsDict, default=str).encode("utf-8"))
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

            amount, hours, days = sc.calculate_price(parkinglot, session_dict)

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


    elif self.path.startswith("/billing/"):
        token = self.headers.get('Authorization')
        session_user = get_session(token)
        if not session_user:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return
        
        if session_user.get('role') != "ADMIN":
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Access denied")
            return

        user = self.path.replace("/billing/", "")
        data = []
        sessions = load_sessions_by_userID(user)

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
            
            amount, hours, days = sc.calculate_price(parkinglot, session_dict)

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
