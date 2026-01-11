import mysql.connector
from DataModels.reservationsModel import Reservations
from datetime import datetime, date, timedelta, time
from decimal import Decimal
from LogicLayer.sessionLogic import start_parking_session

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

def load_reservation_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reservations")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def save_reservation_data(reservation: Reservations):
    if not isinstance(reservation, Reservations):
        raise TypeError("reservation must be of type Reservations")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM reservations ORDER BY id DESC LIMIT 1")
        newest = cursor.fetchone()
        reservation.id = 1 if newest is None else newest["id"] + 1
        data = reservation.to_dict()
        sql = """
        INSERT INTO reservations
            (id, user_id, parking_lot_id, vehicle_id, start_time, end_time,
             status, created_at, cost, updated_at)
        VALUES
            (%(id)s, %(user_id)s, %(parking_lot_id)s, %(vehicle_id)s,
             %(start_time)s, %(end_time)s, %(status)s,
             %(created_at)s, %(cost)s, %(updated_at)s)
        """
        cursor.execute(sql, data)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def update_reservation_data(reservation: Reservations):
    if not isinstance(reservation, Reservations):
        raise TypeError("Expected Reservations instance")
    if reservation.id is None:
        raise ValueError("Reservation must have an 'id' to update")
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = {
        "user_id": reservation.user_id,
        "parking_lot_id": reservation.parking_lot_id,
        "vehicle_id": reservation.vehicle_id,
        "start_time": reservation.start_time,
        "end_time": reservation.end_time,
        "status": reservation.status,
        "created_at": reservation.created_at,
        "cost": reservation.cost,
        "updated_at": reservation.updated_at
    }
    updates = {k: v for k, v in fields.items() if v is not None}
    if not updates:
        return
    sql = f"UPDATE reservations SET {', '.join(f'{k}=%s' for k in updates)} WHERE id=%s"
    values = list(updates.values()) + [reservation.id]
    try:
        cursor.execute(sql, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def delete_reservation(reservation: Reservations):
    if not isinstance(reservation, Reservations):
        raise TypeError("reservation must be a Reservations instance")
    if reservation.id is None:
        raise ValueError("Reservation must have an 'id' to delete")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reservations WHERE id = %s", (reservation.id,))
        conn.commit()
        return {"status": "Deleted", "reservation_id": reservation.id}
    finally:
        cursor.close()
        conn.close()

def get_today_reservations_count_by_lot():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = date.today()
    cursor.execute("""
        SELECT parking_lot_id, COUNT(*) AS count
        FROM reservations
        WHERE DATE(start_time) <= %s
          AND DATE(end_time) >= %s
          AND status='pending'
        GROUP BY parking_lot_id
    """, (today, today))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {str(row["parking_lot_id"]): row["count"] for row in rows}

def get_reservation_by_id(reservation_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM reservations WHERE id = %s", (reservation_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def create_missed_parking_sessions():
    yesterday = (datetime.now() - timedelta(days=1)).date()
    start_dt = datetime.combine(yesterday, time(0, 0, 0))
    end_dt = datetime.combine(yesterday, time(23, 59, 59))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, user_id, vehicle_id, parking_lot_id
            FROM reservations
            WHERE status = 'pending'
              AND DATE(start_time) = %s
            """,
            (yesterday,)
        )
        reservations = cursor.fetchall()

        for r in reservations:
            res_id = r["id"]
            user_id = r["user_id"]
            vehicle_id = r["vehicle_id"]
            parking_lot_id = r["parking_lot_id"]

            cursor.execute(
                "SELECT license_plate FROM vehicles WHERE id = %s",
                (vehicle_id,)
            )
            vehicle = cursor.fetchone()
            if not vehicle:
                continue

            license_plate = vehicle["license_plate"]

            cursor.execute(
                "SELECT daytariff FROM parking_lots WHERE id = %s",
                (parking_lot_id,)
            )
            lot = cursor.fetchone()
            if not lot:
                continue

            daytariff = Decimal(lot["daytariff"])

            result = start_parking_session(
                parking_lot_id=parking_lot_id,
                licenseplate=license_plate,
                user_id=user_id,
                start_time=start_dt,
                end_time=end_dt,
                cost=daytariff
            )

            if result.get("ok"):
                cursor.execute(
                    "UPDATE reservations SET status='confirmed' WHERE id=%s",
                    (res_id,)
                )
                conn.commit()

    finally:
        cursor.close()
        conn.close()

def get_reservation_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT *
            FROM reservations
            WHERE user_id = %s
            AND status = 'pending'
            AND start_time <= %s
            AND end_time >= %s
            ORDER BY start_time ASC
            LIMIT 1
            """, (user_id, datetime.now(), datetime.now()))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def update_status_only(reservation_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE reservations
            SET status = %s,
            updated_at = %s
            WHERE id = %s
            """, ("confirmed", datetime.now(), reservation_id))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def get_reservation_by_user_id_for_confirmed_status(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT *
            FROM reservations
            WHERE user_id = %s
            AND status = 'confirmed'
            ORDER BY start_time ASC
            LIMIT 1
            """, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def cehck_and_update_reservation_status_12_hours():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT *
            FROM reservations
            WHERE status = 'pending'
            AND end_time < NOW()
        """)
        expired_reservations = cursor.fetchall()
        
        for reservation in expired_reservations:
            cursor.execute("""
                UPDATE reservations
                SET status = 'expired'
                WHERE id = %s
            """, (reservation['id'],))
        
        conn.commit()

        return expired_reservations
    
    finally:
        cursor.close()
        conn.close()
