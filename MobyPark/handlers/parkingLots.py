import json
from MobyPark.DataAccesLayer.database_utils_parking_lots import get_db_connection, load_parking_lot_data, load_parking_lot_by_id
from datetime import datetime
from storage_utils import load_json, save_data, load_parking_lot_data, save_parking_lot_data # pyright: ignore[reportUnknownVariableType]
from session_manager import get_session

def do_POST(self):
    token = self.headers.get('Authorization')
    if not token or not get_session(token):
        self.send_response(401)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b"Unauthorized: Invalid or missing session token")
        return

    session_user = get_session(token)
    if 'sessions' in self.path:
        lid = self.path.split("/")[2]
        data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
        sessions = load_json(f'data/pdata/p{lid}-sessions.json', default={})
        if self.path.endswith('start'):
            if 'licenseplate' not in data:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Require field missing", "field": 'licenseplate'}).encode("utf-8"))
                return
            
            filtered = {key: value for key, value in sessions.items() if value.get("licenseplate") == data['licenseplate'] and not value.get('stopped')}
            if len(filtered) > 0:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'Cannot start a session when another sessions for this licesenplate is already started.')
                return
            
            session = {
                "licenseplate": data['licenseplate'],
                "started": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "stopped": None,
                "user": session_user["username"]
            }
            sessions[str(len(sessions) + 1)] = session
            save_data(f'data/pdata/p{lid}-sessions.json', sessions)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(f"Session started for: {data['licenseplate']}".encode('utf-8'))

        elif self.path.endswith('stop'):
            if 'licenseplate' not in data:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Require field missing", "field": 'licenseplate'}).encode("utf-8"))
                return
            
            filtered = {key: value for key, value in sessions.items() if value.get("licenseplate") == data['licenseplate'] and not value.get('stopped')}
            if len(filtered) < 0:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'Cannot stop a session when there is no session for this licesenplate.')
                return
            
            sid = next(iter(filtered))
            sessions[sid]["stopped"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            save_data(f'data/pdata/p{lid}-sessions.json', sessions)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(f"Session stopped for: {data['licenseplate']}".encode('utf-8'))

    else:
        if not 'ADMIN' == session_user.get('role'):
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Access denied")
            return
        
        data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
        parking_lots = load_parking_lot_data()
        new_lid = str(len(parking_lots) + 1)
        parking_lots[new_lid] = data
        save_parking_lot_data(parking_lots)
        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(f"Parking lot saved under ID: {new_lid}".encode('utf-8'))

def do_PUT(self):
    lid = self.path.split("/")[2]
    parking_lots = load_parking_lot_data()
    if lid:
        if lid in parking_lots:
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)
            if not 'ADMIN' == session_user.get('role'):
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Access denied")
                return
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            parking_lots[lid] = data
            save_parking_lot_data(parking_lots)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Parking lot modified")
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Parking lot not found")
            return

def do_DELETE(self):
    lid = self.path.split("/")[2]
    parking_lots = load_parking_lot_data()
    if lid:
        if lid in parking_lots:
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)
            if not 'ADMIN' == session_user.get('role'):
                self.send_response(403)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Access denied")
                return
            if 'sessions' in self.path:
                sessions = load_json(f'data/pdata/p{lid}-sessions.json', default={})
                sid = self.path.split("/")[-1]
                if sid.isnumeric():
                    del sessions[sid]
                    save_data(f'data/pdata/p{lid}-sessions.json', sessions)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Sessions deleted")
                else:
                    self.send_response(403)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Session ID is required, cannot delete all sessions")
            else:
                del parking_lots[lid]
                save_parking_lot_data(parking_lots)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Parking lot deleted")
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Parking lot not found")
            return

def do_GET(self):
    parts = self.path.strip("/").split("/")

    if len(parts) == 1 and parts[0] == "parking-lots":
        parking_lots = load_parking_lot_data()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(parking_lots, default=str).encode("utf-8"))
        return

    elif len(parts) == 2 and parts[0] == "parking-lots":
        lid = parts[1]
        lot = load_parking_lot_by_id(lid)
        if lot:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(lot, default=str).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Parking lot not found")
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")

def do_POST(self):
    parts = self.path.strip("/").split("/")

    if parts == ["parking-lots"]:
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Invalid JSON format")
            return

        required_fields = ["name", "location", "address", "capacity", "tariff"]
        if not all(field in data for field in required_fields):
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Missing required fields")
            return

        name = data["name"]
        location = data["location"]
        address = data["address"]
        capacity = data["capacity"]
        tariff = data["tariff"]
        reserved = data.get("reserved", 0)
        daytariff = data.get("daytariff", 0)
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        status = data.get("status", "open")
        closed_reason = data.get("closed_reason")
        closed_date = data.get("closed_date")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO parking_lots
                (name, location, address, capacity, reserved, tariff, daytariff,
                 created_at, latitude, longitude, status, closed_reason, closed_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s)
                """,
                (name, location, address, capacity, reserved, tariff, daytariff,
                 latitude, longitude, status, closed_reason, closed_date)
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            conn.close()

            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"id": new_id, "message": "Parking lot created"}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        return

    elif parts == ["parking-lots", "sessions", "start"]:
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode("utf-8"))

        required_fields = ["parking_lot_id", "licenseplate"]
        if not all(f in data for f in required_fields):
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Missing required fields")
            return

        parking_lot_id = data["parking_lot_id"]
        licenseplate = data["licenseplate"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, checked_out FROM vehicles WHERE license_plate = %s", (licenseplate,))
        vehicle = cursor.fetchone()
        if not vehicle:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Vehicle not found")
            cursor.close()
            conn.close()
            return

        if vehicle["checked_out"]:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Vehicle already checked out")
            cursor.close()
            conn.close()
            return

        user_id = vehicle["user_id"]
        cursor.execute(
            "INSERT INTO parking_sessions (parking_lot_id, licenseplate, started, stopped, user, duration_minutes, cost, payment_status) "
            "VALUES (%s, %s, NOW(), NULL, %s, 0, 0, 'pending')",
            (parking_lot_id, licenseplate, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": f"Session started for: {licenseplate}"}).encode("utf-8"))
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")

def do_PUT(self):
    parts = self.path.strip("/").split("/")

    if parts == ["parking-lots", "sessions", "stop"]:
        content_length = int(self.headers.get("Content-Length", 0))
        put_data = self.rfile.read(content_length)
        data = json.loads(put_data.decode("utf-8"))

        required_fields = ["parking_lot_id", "licenseplate"]
        if not all(f in data for f in required_fields):
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Missing required fields")
            return

        parking_lot_id = data["parking_lot_id"]
        licenseplate = data["licenseplate"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM vehicles WHERE license_plate = %s", (licenseplate,))
        vehicle = cursor.fetchone()
        if not vehicle:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Vehicle not found")
            cursor.close()
            conn.close()
            return

        user_id = vehicle["user_id"]
        cursor.execute(
            "SELECT * FROM parking_sessions WHERE parking_lot_id = %s AND licenseplate = %s AND stopped IS NULL",
            (parking_lot_id, licenseplate)
        )
        session = cursor.fetchone()
        if not session:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"No active session found for this vehicle")
            cursor.close()
            conn.close()
            return

        cursor.execute("SELECT tariff FROM parking_lots WHERE id = %s", (parking_lot_id,))
        lot = cursor.fetchone()
        tariff = lot['tariff'] if lot else 0

        cursor.execute(
            "UPDATE parking_sessions "
            "SET stopped = NOW(), duration_minutes = TIMESTAMPDIFF(MINUTE, started, NOW()), "
            "cost = TIMESTAMPDIFF(MINUTE, started, NOW()) * %s / 60, payment_status = 'unpaid' "
            "WHERE id = %s",
            (tariff, session['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": f"Session stopped for: {licenseplate}"}).encode("utf-8"))
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")

def do_PUT_parking_lot(self, lot_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parking_lots WHERE id = %s", (lot_id,))
    lot = cursor.fetchone()
    if not lot:
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"Parking lot not found")
        cursor.close()
        conn.close()
        return

    allowed_fields = ["name", "location", "address", "capacity", "reserved",
                      "tariff", "daytariff", "latitude", "longitude",
                      "status", "closed_reason", "closed_date"]

    updates = []
    values = []
    for key, value in data.items():
        if key in allowed_fields:
            updates.append(f"{key} = %s")
            values.append(value)

    if not updates:
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"No valid fields to update")
        cursor.close()
        conn.close()
        return

    values.append(lot_id)
    query = f"UPDATE parking_lots SET {', '.join(updates)} WHERE id = %s"
    cursor.execute(query, tuple(values))
    conn.commit()
    cursor.close()
    conn.close()

    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps({"message": "Parking lot updated"}).encode("utf-8"))

def do_DELETE(self):
    parts = self.path.strip("/").split("/")
    if len(parts) == 2 and parts[0] == "parking-lots":
        lot_id = parts[1]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM parking_lots WHERE id = %s", (lot_id,))
        if not cursor.fetchone():
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Parking lot not found")
            cursor.close()
            conn.close()
            return

        cursor.execute("DELETE FROM parking_lots WHERE id = %s", (lot_id,))
        conn.commit()
        cursor.close()
        conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Parking lot deleted"}).encode("utf-8"))
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")
