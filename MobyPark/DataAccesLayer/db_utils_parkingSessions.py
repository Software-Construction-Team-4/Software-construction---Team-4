from datetime import datetime
import mysql.connector
from DataModels.parkingSessionModel import ParkingSession
from session_calculator import calculate_price


def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

def _row_to_parking_session(row):
    return ParkingSession(
        id=row["id"],
        parking_lot_id=row["parking_lot_id"],
        session=row["session"],
        user_id=row["user"],
        licenseplate=row["licenseplate"],
        started=row["started"],
        stopped=row["stopped"],
        duration_minutes=row["duration_minutes"],
        cost=row["cost"],
        payment_status=row["payment_status"]
    )

def start_session(parking_lot_id, licenseplate, user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(
            """
            SELECT id, parking_lot_id, started
            FROM parking_sessions
            WHERE licenseplate = %s AND stopped IS NULL
            LIMIT 1
            """,
            (licenseplate,)
        )
        existing = cursor.fetchone()
        if existing:
            return {
                "ok": False,
                "error": "Active session already exists for this license plate",
                "active_session": {
                    "id": existing["id"],
                    "parking_lot_id": existing["parking_lot_id"],
                    "started": existing["started"],
                }
            }

        cursor.execute(
            "SELECT COALESCE(MAX(session), 0) + 1 AS next_num FROM parking_sessions WHERE parking_lot_id=%s",
            (parking_lot_id,)
        )
        next_session_number = cursor.fetchone()["next_num"]

        cursor.execute(
            """
            INSERT INTO parking_sessions
              (parking_lot_id, licenseplate, started, user, duration_minutes, cost, payment_status, session)
            VALUES
              (%s, %s, %s, %s, 0, 0, 'pending', %s)
            """,
            (parking_lot_id, licenseplate, datetime.now(), user_id, next_session_number)
        )

        cursor.execute(
            "UPDATE parking_lots SET active_sessions = COALESCE(active_sessions,0) + 1 WHERE id=%s",
            (parking_lot_id,)
        )

        conn.commit()
        return {"ok": True, "session_id": cursor.lastrowid}
    finally:
        cursor.close()
        conn.close()


def stop_session(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""SELECT * FROM parking_sessions WHERE user = %s AND stopped IS NULL""", 
        (user_id,))
        session = cursor.fetchone()

        if not session:
            return None

        cursor.execute("SELECT * FROM parking_lots WHERE id = %s", (session["parking_lot_id"],))
        lot = cursor.fetchone()

        stopped: datetime = datetime.now()
        duration = stopped - session["started"]
        minutes = int(duration.total_seconds() / 60)
        price, hour, days = calculate_price(lot, session)

        cursor.execute(
            """
            UPDATE parking_sessions
            SET
              stopped = %s,
              duration_minutes = %s,
              cost = %s,
              payment_status = 'unpaid'
            WHERE id = %s
            """,
            (stopped, minutes, price, session["id"])
        )

        cursor.execute(
            "UPDATE parking_lots SET active_sessions = GREATEST(COALESCE(active_sessions,0)-1,0) WHERE id=%s",
            (session["parking_lot_id"],)
        )

        conn.commit()

        cursor.execute("SELECT * FROM parking_sessions WHERE id=%s", (session["id"],))
        updated_session = cursor.fetchone()
        return _row_to_parking_session(updated_session)
    finally:
        cursor.close()
        conn.close()


def load_sessions(parking_lot_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        if parking_lot_id:
            cursor.execute("SELECT * FROM parking_sessions WHERE parking_lot_id=%s", (parking_lot_id,))
        else:
            cursor.execute("SELECT * FROM parking_sessions")

        rows = cursor.fetchall()
        return {str(row["id"]): _row_to_parking_session(row) for row in rows}
    finally:
        cursor.close()
        conn.close()


def load_sessions_by_userID(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT * FROM parking_sessions WHERE user=%s", (id,))
        rows = cursor.fetchall()
        return [_row_to_parking_session(row) for row in rows]
    finally:
        cursor.close()
        conn.close()

def update_payment_status(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE parking_sessions
            SET payment_status = %s
            WHERE user = %s
            AND stopped IS NOT NULL
            """, 
            ("paid", user_id))

        conn.commit()
        return

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
