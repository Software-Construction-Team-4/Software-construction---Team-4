import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

def load_parking_lots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM parking_lots")
        rows = cursor.fetchall()
        return {str(row["id"]): row for row in rows}
    finally:
        cursor.close()
        conn.close()

def load_parking_lot_by_id(lot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM parking_lots WHERE id=%s", (lot_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def save_parking_lot(lot_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO parking_lots
        (name, location, address, capacity, reserved, tariff, daytariff, latitude, longitude, status, closed_reason, closed_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (
            lot_data.get("name"),
            lot_data.get("location"),
            lot_data.get("address"),
            lot_data.get("capacity"),
            lot_data.get("reserved", 0),
            lot_data.get("tariff", 0),
            lot_data.get("daytariff", 0),
            lot_data.get("latitude"),
            lot_data.get("longitude"),
            lot_data.get("status", "open"),
            lot_data.get("closed_reason"),
            lot_data.get("closed_date")
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
        allowed_fields = ["name","location","address","capacity","reserved","tariff","daytariff","latitude","longitude","status","closed_reason","closed_date"]
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
