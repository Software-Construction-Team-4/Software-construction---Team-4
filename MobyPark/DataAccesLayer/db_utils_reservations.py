import mysql.connector
from DataModels.reservationsModel import Reservations

# def get_db_connection():
#     return mysql.connector.connect(
#         host="145.24.237.71",
#         port=8001,
#         user="vscode",
#         password="StrongPassword123!",
#         database="mobypark"
#     )

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Kikkervis66!",
        database="mobypark"
    )


def load_parking_lot_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parking_lots")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    parking_lots = {str(row["id"]): row for row in rows}
    return parking_lots


def save_parking_lot_data(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    if data:

        if isinstance(data, dict):
            data = list(data.values())

        for d in data:
            d.pop("id", None)

        keys = data[0].keys()
        columns = ", ".join(keys)
        placeholders = ", ".join(["%s"] * len(keys))
        sql = f"INSERT INTO parking_lots ({columns}) VALUES ({placeholders})"

        values = [tuple(d[k] for k in keys) for d in data]

        cursor.executemany(sql, values)

    conn.commit()
    cursor.close()
    conn.close()



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

    data = reservation.to_dict()

    data.pop("id", None)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
        INSERT INTO reservations
            (user_id, parking_lot_id, vehicle_id, start_time, end_time,
             status, created_at, cost, updated_at)
        VALUES
            (%(user_id)s, %(parking_lot_id)s, %(vehicle_id)s, %(start_time)s, %(end_time)s,
             %(status)s, %(created_at)s, %(cost)s, %(updated_at)s)
        """
        cursor.execute(sql, data)
        conn.commit()

    except Exception as e:
        print(f"Error saving reservation: {e}")

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

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        rid = reservation.id
        if rid is None:
            raise ValueError("Reservation must have an 'id' to delete")

        sql = "DELETE FROM reservations WHERE id = %s"
        cursor.execute(sql, (rid,))
        conn.commit()

        print(f"Reservation {rid} deleted successfully.")
        return {"status": "Deleted", "reservation_id": rid}

    except mysql.connector.Error as e:
        print(f"Error deleting reservation: {e}")
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()












