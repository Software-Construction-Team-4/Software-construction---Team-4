import json
from database_utils import load_parking_lot_data, load_parking_lot_by_id

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
