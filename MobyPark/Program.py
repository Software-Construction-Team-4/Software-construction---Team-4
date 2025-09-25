import json
import hashlib
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from storage_utils import load_json, save_data, save_user_data, load_parking_lot_data, save_parking_lot_data, save_reservation_data, load_reservation_data, load_payment_data, save_payment_data # pyright: ignore[reportUnknownVariableType]
from session_manager import add_session, remove_session, get_session # pyright: ignore[reportUnknownVariableType]
import session_calculator as sc

def ReservationsToDict():
    reservations = load_reservation_data()
    newreservations = {r["id"]: r for r in reservations}
    save_reservation_data(newreservations)

#ReservationsToDict()


