import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
<<<<<<<< HEAD:MobyPark/DataAccesLayer/database_utils_parking_lots.py
        user="root",
        password="Des2106Sta123!",
========
        user="vscode",
        password="StrongPassword123!",
>>>>>>>> origin/database-working-and-all-db-code-fixed:MobyPark/db_utils_parkingLots.py
        database="mobypark"
    )

def load_parking_lot_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parking_lots")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {str(row['id']): row for row in rows}

def load_parking_lot_by_id(lid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parking_lots WHERE id = %s", (lid,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def start_parking_session(parking_lot_id, licenseplate, user):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO parking_sessions (parking_lot_id, licenseplate, started, stopped, user, duration_minutes, cost, payment_status) "
        "VALUES (%s, %s, NOW(), NULL, %s, 0, 0, 'pending')",
        (parking_lot_id, licenseplate, user)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id

def stop_parking_session(parking_lot_id, licenseplate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM parking_sessions WHERE parking_lot_id=%s AND licenseplate=%s AND stopped IS NULL",
        (parking_lot_id, licenseplate)
    )
    session = cursor.fetchone()
    if not session:
        cursor.close()
        conn.close()
        return None

    cursor.execute(
        "SELECT tariff FROM parking_lots WHERE id=%s",
        (parking_lot_id,)
    )
    lot = cursor.fetchone()
    tariff = lot['tariff'] if lot else 0

    cursor.execute(
        "UPDATE parking_sessions SET stopped=NOW(), duration_minutes=TIMESTAMPDIFF(MINUTE, started, NOW()), "
        "cost=TIMESTAMPDIFF(MINUTE, started, NOW())*%s, payment_status='unpaid' "
        "WHERE id=%s",
        (tariff / 60, session['id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return session

