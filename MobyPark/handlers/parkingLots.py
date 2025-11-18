import json
from DataAccesLayer.db_utils_parkingLots import (
    load_parking_lots,
    load_parking_lot_by_id,
    save_parking_lot,
    update_parking_lot,
    delete_parking_lot
)
from . import parkingSessions

def do_GET(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) > 1 and parts[1] == "sessions":
        return parkingSessions.do_GET(self)

    if parts[0] == "parking-lots":
        if len(parts) == 1:
            lots = load_parking_lots()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(lots).encode("utf-8"))
            return
        if len(parts) == 2:
            lot = load_parking_lot_by_id(parts[1])
            if lot:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(lot).encode("utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"Not found")
            return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")

def do_POST(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) > 1 and parts[1] == "sessions":
        return parkingSessions.do_POST(self)

    if self.path == "/parking-lots":
        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))
        new_id = save_parking_lot(data)
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"id": new_id}).encode("utf-8"))
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")

def do_PUT(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) == 2:
        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))
        update_parking_lot(parts[1], data)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"Updated")
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")

def do_DELETE(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) == 2:
        delete_parking_lot(parts[1])
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"Deleted")
        return

    self.send_response(404)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(b"Invalid route")
