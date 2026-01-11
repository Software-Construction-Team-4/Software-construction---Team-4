from datetime import datetime
from DataAccesLayer.db_utils_parkingSessions import (
    get_db_connection,
    create_parking_session_from_row,
    find_active_session_by_licenseplate,
    get_next_session_number,
    insert_parking_session,
    increase_active_sessions,
    find_active_session_by_user,
    update_session_on_stop,
    decrease_active_sessions,
    get_parking_lot,
    get_session_by_id,
    load_sessions_by_user,
    mark_sessions_as_paid,
    get_unpaid_session_for_user,
    mark_session_as_refunded
)
from session_calculator import calculate_price


def start_parking_session(parking_lot_id, licenseplate, user_id, start_time=None, end_time=None, cost=None):
    connection = get_db_connection()
    try:
        existing = find_active_session_by_licenseplate(connection, licenseplate)
        if existing:
            return {
                "error": "This vehicle is already parked",
                "active_session": {"licenseplate": existing["licenseplate"]}
            }

        session_number = get_next_session_number(connection, parking_lot_id)

        session_data = {
            "parking_lot_id": parking_lot_id,
            "licenseplate": licenseplate,
            "started": start_time or datetime.now(),
            "stopped": end_time,
            "user_id": user_id,
            "cost": cost if cost is not None else 0,
            "session_number": session_number
        }

        session_id = insert_parking_session(connection, session_data)
        increase_active_sessions(connection, parking_lot_id)

        connection.commit()
        return {"ok": True, "session_id": session_id}
    finally:
        connection.close()


def stop_parking_session(user_id):
    connection = get_db_connection()
    try:
        session_row = find_active_session_by_user(connection, user_id)
        if not session_row:
            return None

        lot = get_parking_lot(connection, session_row["parking_lot_id"])

        stopped = datetime.now()
        duration = stopped - session_row["started"]
        minutes = int(duration.total_seconds() / 60)
        price, _, _ = calculate_price(lot, session_row)

        update_session_on_stop(connection, session_row["id"], stopped, minutes, price)
        decrease_active_sessions(connection, session_row["parking_lot_id"])

        connection.commit()

        updated = get_session_by_id(connection, session_row["id"])
        return create_parking_session_from_row(updated)
    finally:
        connection.close()


def load_sessions_for_user(user_id):
    connection = get_db_connection()
    try:
        rows = load_sessions_by_user(connection, user_id)
        return [create_parking_session_from_row(item) for item in rows]
    finally:
        connection.close()


def mark_user_sessions_paid(user_id):
    connection = get_db_connection()
    try:
        mark_sessions_as_paid(connection, user_id)
        connection.commit()
    finally:
        connection.close()


def get_unpaid_session(user_id):
    connection = get_db_connection()
    try:
        row = get_unpaid_session_for_user(connection, user_id)
        return create_parking_session_from_row(row) if row else None
    finally:
        connection.close()


def refund_session(session_id):
    connection = get_db_connection()
    try:
        mark_session_as_refunded(connection, session_id)
        connection.commit()
    finally:
        connection.close()
