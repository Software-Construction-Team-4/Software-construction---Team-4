import mysql.connector
from DataModels.parkingLotsModel import ParkingLot
from DataAccesLayer.db_utils_reservations import get_today_reservations_count_by_lot

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

def _row_to_parking_lot(row):
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

def load_parking_lots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM parking_lots")
        rows = cursor.fetchall()
        today_reserved = get_today_reservations_count_by_lot()


        lots = {}
        for row in rows:
            lot_id = str(row["id"])
            reserved_count = today_reserved.get(lot_id, 0)
            row["reserved"] = reserved_count
            update_parking_lot(lot_id, {"reserved": reserved_count})

            cursor.execute(
                "SELECT COUNT(*) as active_count FROM parking_sessions WHERE parking_lot_id=%s AND stopped IS NULL",
                (lot_id,)
            )
            active_count = cursor.fetchone()["active_count"]
            row["active_sessions"] = active_count
            update_parking_lot(lot_id, {"active_sessions": active_count})

            lots[lot_id] = _row_to_parking_lot(row)

        return lots
    finally:
        cursor.close()
        conn.close()

def load_parking_lot_by_id(lot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM parking_lots WHERE id=%s", (lot_id,))
        row = cursor.fetchone()
        if not row:
            return None

        today_reserved = get_today_reservations_count_by_lot()
        reserved_count = today_reserved.get(str(lot_id), 0)
        row["reserved"] = reserved_count
        update_parking_lot(lot_id, {"reserved": reserved_count})

        cursor.execute(
            "SELECT COUNT(*) as active_count FROM parking_sessions WHERE parking_lot_id=%s AND stopped IS NULL",
            (lot_id,)
        )
        active_count = cursor.fetchone()["active_count"]
        row["active_sessions"] = active_count
        update_parking_lot(lot_id, {"active_sessions": active_count})

        return _row_to_parking_lot(row)
    finally:
        cursor.close()
        conn.close()

def save_parking_lot(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO parking_lots
        (name, location, address, capacity, reserved, tariff, daytariff, latitude, longitude, status, closed_reason, closed_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (
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
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def update_parking_lot(lot_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        allowed_fields = ["name","location","address","capacity","reserved","tariff","daytariff","latitude","longitude","status","closed_reason","closed_date","active_sessions"]
        updates = [f"{k}=%s" for k in data if k in allowed_fields]
        values = [data[k] for k in data if k in allowed_fields]
        if updates:
            values.append(lot_id)
            sql = f"UPDATE parking_lots SET {', '.join(updates)} WHERE id=%s"
            cursor.execute(sql, tuple(values))
            conn.commit()
    finally:
        cursor.close()
        conn.close()

def delete_parking_lot(lot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM parking_lots WHERE id=%s", (lot_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def increment_active_sessions(lot_id, delta=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE parking_lots SET active_sessions = GREATEST(COALESCE(active_sessions,0) + %s, 0) WHERE id=%s",
            (delta, lot_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
