import json
from DataAccesLayer.db_utils_parkingLots import (
    load_parking_lots,
    load_parking_lot_by_id,
    save_parking_lot,
    update_parking_lot,
    delete_parking_lot
)
from . import parkingSessions


def send_json(self, status_code, data):
    self.send_response(status_code)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    # default=str fixes Decimal and datetime
    self.wfile.write(json.dumps(data, default=str).encode("utf-8"))


def do_GET(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) > 1 and parts[1] == "sessions":
        return parkingSessions.do_GET(self)

    if parts[0] == "parking-lots":
        if len(parts) == 1:
            lots = load_parking_lots()  # dict[id] -> ParkingLot
            lots_serialized = {
                lot_id: lot.__dict__ for lot_id, lot in lots.items()
            }
            return send_json(self, 200, lots_serialized)

        if len(parts) == 2:
            lot = load_parking_lot_by_id(parts[1])  # ParkingLot or None
            if lot:
                return send_json(self, 200, lot.__dict__)
            else:
                return send_json(self, 404, {"error": "Not found"})

    return send_json(self, 404, {"error": "Invalid route"})


def do_POST(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) > 1 and parts[1] == "sessions":
        return parkingSessions.do_POST(self)

    if self.path == "/parking-lots":
        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))
        new_id = save_parking_lot(data)
        return send_json(self, 201, {"id": new_id})

    return send_json(self, 404, {"error": "Invalid route"})


def do_PUT(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) == 2:
        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))
        update_parking_lot(parts[1], data)
        return send_json(self, 200, {"message": "Updated"})

    return send_json(self, 404, {"error": "Invalid route"})


def do_DELETE(self):
    parts = self.path.strip("/").split("/")
    if parts[0] == "parking-lots" and len(parts) == 2:

        lot = load_parking_lot_by_id(parts[1])
        if not lot:
            return send_json(self, 404, {"error": "Parking lot does not exist"})

        delete_parking_lot(parts[1])
        return send_json(self, 200, {"message": "Deleted"})

    return send_json(self, 404, {"error": "Invalid route"})
