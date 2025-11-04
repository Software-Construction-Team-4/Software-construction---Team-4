import json
from database_utils import get_db_connection, load_parking_lot_data, load_parking_lot_by_id

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

    daytariff = data.get("daytariff", 0)
    reserved = data.get("reserved", 0)
    latitude = data.get("latitude", None)
    longitude = data.get("longitude", None)
    status = data.get("status", "open")
    closed_reason = data.get("closed_reason", None)
    closed_date = data.get("closed_date", None)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO parking_lots
            (name, location, address, capacity, reserved, tariff, daytariff, created_at, latitude, longitude, status, closed_reason, closed_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s)
            """,
            (
                name, location, address, capacity, reserved,
                tariff, daytariff, latitude, longitude,
                status, closed_reason, closed_date
            ),
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

def do_DELETE(self):
    parts = self.path.strip("/").split("/")

    if len(parts) == 2 and parts[0] == "parking-lots":
        lot_id = parts[1]
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM parking_lots WHERE id = %s", (lot_id,))
            existing = cursor.fetchone()

            if not existing:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"Parking lot not found")
                return

            cursor.execute("DELETE FROM parking_lots WHERE id = %s", (lot_id,))
            conn.commit()

            cursor.close()
            conn.close()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Parking lot deleted"}).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")
