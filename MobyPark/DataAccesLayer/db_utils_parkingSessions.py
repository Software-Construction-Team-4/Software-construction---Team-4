import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
    )

def start_session(parking_lot_id, licenseplate, user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO parking_sessions (parking_lot_id, licenseplate, started, user, duration_minutes, cost, payment_status) "
            "VALUES (%s, %s, NOW(), %s, 0, 0, 'pending')",
            (parking_lot_id, licenseplate, user_id)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def stop_session(parking_lot_id, licenseplate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM parking_sessions WHERE parking_lot_id=%s AND licenseplate=%s AND stopped IS NULL",
            (parking_lot_id, licenseplate)
        )
        session = cursor.fetchone()
        if not session:
            return None

        cursor.execute("SELECT tariff FROM parking_lots WHERE id=%s", (parking_lot_id,))
        lot = cursor.fetchone()
        tariff = lot['tariff'] if lot else 0

        cursor.execute(
            "UPDATE parking_sessions SET stopped=NOW(), duration_minutes=TIMESTAMPDIFF(MINUTE, started, NOW()), "
            "cost=TIMESTAMPDIFF(MINUTE, started, NOW()) * %s / 60, payment_status='unpaid' "
            "WHERE id=%s",
            (tariff, session['id'])
        )
        conn.commit()
        return session
    finally:
        cursor.close()
        conn.close()

def load_sessions(parking_lot_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if parking_lot_id:
            cursor.execute("SELECT * FROM parking_sessions WHERE parking_lot_id=%s", (parking_lot_id,))
        else:
            cursor.execute("SELECT * FROM parking_sessions")
        rows = cursor.fetchall()
        return {str(row['id']): row for row in rows}
    finally:
        cursor.close()
        conn.close()
