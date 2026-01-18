import mysql.connector
from DataModels.parkingLotsModel import ParkingLot

from environment import Environment
def get_db_connection():
    return mysql.connector.connect(
        host=Environment.get_var("DB_HOST"),
        port=int(Environment.get_var("DB_PORT")),
        user=Environment.get_var("DB_USER"),
        password=Environment.get_var("DB_PASSWORD"),
        database=Environment.get_var("DB_NAME")
    )

def create_parking_lot_from_row(row):
    return ParkingLot(
        id=row["id"],
        name=row["name"],
        location=row["location"],
        address=row["address"],
        capacity=row["capacity"],
        active_sessions=row.get("active_sessions", 0) or 0,
        reserved=row.get("reserved", 0) or 0,
        tariff=row.get("tariff", 0),
        daytariff=row.get("daytariff", 0),
        created_at=row.get("created_at"),
        latitude=row.get("latitude"),
        longitude=row.get("longitude"),
        status=row.get("status"),
        closed_reason=row.get("closed_reason"),
        closed_date=row.get("closed_date"),
    )

def load_all_parking_lots_from_db():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM parking_lots")
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def load_parking_lot_row_by_id(lot_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM parking_lots WHERE id=%s", (lot_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def save_parking_lot(data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO parking_lots
            (name, location, address, capacity, reserved, tariff, daytariff,
             latitude, longitude, status, closed_reason, closed_date)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                data.get("name"),
                data.get("location"),
                data.get("address"),
                data.get("capacity"),
                data.get("reserved", 0),
                data.get("tariff", 0),
                data.get("daytariff", 0),
                data.get("latitude"),
                data.get("longitude"),
                data.get("status", "open"),
                data.get("closed_reason"),
                data.get("closed_date")
            )
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()

def update_parking_lot(lot_id, data):
    allowed_fields = [
        "name","location","address","capacity","reserved",
        "tariff","daytariff","latitude","longitude",
        "status","closed_reason","closed_date","active_sessions"
    ]

    update_parts = []
    update_values = []

    for field in data:
        if field in allowed_fields:
            update_parts.append(f"{field}=%s")
            update_values.append(data[field])

    if not update_parts:
        return

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        update_values.append(lot_id)
        cursor.execute(
            f"UPDATE parking_lots SET {', '.join(update_parts)} WHERE id=%s",
            tuple(update_values)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_parking_lot(lot_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM parking_lots WHERE id=%s", (lot_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def increment_active_sessions(lot_id, delta=1):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE parking_lots
            SET active_sessions = GREATEST(COALESCE(active_sessions,0) + %s, 0)
            WHERE id=%s
            """,
            (delta, lot_id)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def increment_reserved(lot_id, delta):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE parking_lots
            SET reserved = GREATEST(COALESCE(reserved,0) + %s, 0)
            WHERE id=%s
            """,
            (delta, lot_id)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def parking_lot_exists(lot_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM parking_lots WHERE id=%s LIMIT 1",
            (lot_id,)
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        connection.close()

def load_active_session_count(lot_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS active_sessions
            FROM parking_sessions
            WHERE parking_lot_id=%s AND stopped IS NULL
            """,
            (lot_id,)
        )
        return cursor.fetchone()["active_sessions"]
    finally:
        cursor.close()
        connection.close()
