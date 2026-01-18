from DataAccesLayer.db_utils_reservations import load_all_reservations, get_reservation_by_id, save_reservation, update_reservation, delete_reservation, get_today_reservations_count_by_lot, create_missed_parking_sessions_for_date
from DataModels.reservationsModel import Reservations
from datetime import date, datetime

def get_all_reservations():
    rows = load_all_reservations()
    reservations = []
    for r in rows:
        reservations.append(
            Reservations(
                id=r["id"],
                user_id=r["user_id"],
                parking_lot_id=r["parking_lot_id"],
                vehicle_id=r["vehicle_id"],
                start_time=r["start_time"],
                end_time=r["end_time"],
                status=r["status"],
                created_at=r.get("created_at"),
                cost=r.get("cost"),
                updated_at=r.get("updated_at")
            )
        )
    return reservations

def get_reservation(rid):
    row = get_reservation_by_id(rid)
    if not row:
        return None
    return Reservations(
        id=row["id"],
        user_id=row["user_id"],
        parking_lot_id=row["parking_lot_id"],
        vehicle_id=row["vehicle_id"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        status=row["status"],
        created_at=row.get("created_at"),
        cost=row.get("cost"),
        updated_at=row.get("updated_at")
    )

def create_reservation(reservation: Reservations):
    reservation_id = save_reservation(reservation)
    return reservation_id

def update_reservation_logic(reservation: Reservations):
    update_reservation(reservation)

def delete_reservation_logic(reservation_id):
    delete_reservation(reservation_id)

def get_reservations_count_today():
    return get_today_reservations_count_by_lot()

def process_missed_sessions(target_date: date):
    create_missed_parking_sessions_for_date(target_date)

def get_reservation_by_user_id(user_id):
    all_reservations = load_all_reservations()
    for r in all_reservations:
        if r["user_id"] == user_id and r["status"] == "pending":
            return Reservations(
                id=r["id"],
                user_id=r["user_id"],
                parking_lot_id=r["parking_lot_id"],
                vehicle_id=r["vehicle_id"],
                start_time=r["start_time"],
                end_time=r["end_time"],
                status=r["status"],
                created_at=r.get("created_at"),
                cost=r.get("cost"),
                updated_at=r.get("updated_at")
            )
    return None
