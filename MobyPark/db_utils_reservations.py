import mysql.connector
import os

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


def save_reservation_data(data):
    if not data:
        print("No data to insert.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    db_columns = [
        "user_id",
        "parking_lot_id",
        "vehicle_id",
        "start_time",
        "end_time",
        "status",
        "created_at",
        "cost",
        "updated_at"
    ]

    filtered_data = []
    for d in data:
        d = d.copy()
        d.pop("id", None)

        if "updated_at" not in d:
            d["updated_at"] = None

        row = {col: d.get(col) for col in db_columns}
        filtered_data.append(row)

    keys = filtered_data[0].keys()
    columns = ", ".join(keys)
    placeholders = ", ".join(["%s"] * len(keys))
    sql = f"INSERT INTO reservations ({columns}) VALUES ({placeholders})"

    values = [tuple(row[k] for k in keys) for row in filtered_data]

    try:
        cursor.executemany(sql, values)
        conn.commit()
        print("Reservation(s) inserted successfully!")
    except mysql.connector.Error as e:
        print("Error inserting reservation:", e)
    finally:
        cursor.close()
        conn.close()


def update_reservation_data(reservation):
    if "id" not in reservation:
        raise ValueError("Reservation must have an 'id' to update")

    conn = get_db_connection()
    cursor = conn.cursor()

    db_columns = [
        "user_id",
        "parking_lot_id",
        "vehicle_id",
        "start_time",
        "end_time",
        "status",
        "updated_at",
        "cost"
    ]

    set_clause = ", ".join(f"{col}=%s" for col in db_columns)
    sql = f"UPDATE reservations SET {set_clause} WHERE id=%s"

    values = [reservation[col] for col in db_columns]
    values.append(reservation["id"])

    try:
        cursor.execute(sql, values)
        conn.commit()
        print(f"Reservation {reservation['id']} updated successfully!")
    except mysql.connector.Error as e:
        print("Error updating reservation:", e)
    finally:
        cursor.close()
        conn.close()

def delete_reservation(reservation):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        rid = int(reservation["id"])
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












