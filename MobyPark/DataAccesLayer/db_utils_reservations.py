import mysql.connector
from DataModels.reservationsModel import Reservations
from datetime import date

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

# def get_db_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         port=3306,
#         user="root",
#         password="Kikkervis66!",
#         database="mobypark"
#     )

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
          AND status = 'confirmed'
        GROUP BY parking_lot_id
    """, (today, today))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return {str(row["parking_lot_id"]): row["count"] for row in rows}
