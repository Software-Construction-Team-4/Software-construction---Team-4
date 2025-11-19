import mysql.connector
from mysql.connector import Error
from datetime import datetime

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="145.24.237.71",
            port=8001,
            user="vscode",
            password="StrongPassword123!",
            database="mobypark"
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None


def load_json(filename: str, default=[]):
    conn = get_db_connection()
    if conn is None:
        return default

    cursor = conn.cursor(dictionary=True)

    if "vehicles" in filename:
        query = "SELECT * FROM vehicles"
    elif "users" in filename:
        query = "SELECT * FROM users"
    elif "parking-lots" in filename:
        query = "SELECT * FROM parking_lots"
    elif "reservations" in filename:
        query = "SELECT * FROM reservations"
    elif "payments" in filename:
        query = "SELECT * FROM payments"
    else:
        cursor.close()
        conn.close()
        return default

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def save_data(filename: str, data):
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()

    try:
        if "vehicles" in filename:
            for v in data:

                cursor.execute("SELECT id FROM vehicles WHERE id=%s", (v.get("id"),))
                exists = cursor.fetchone()

                if exists:
                    cursor.execute("""
                        UPDATE vehicles SET
                            user_id=%s,
                            license_plate=%s,
                            make=%s,
                            model=%s,
                            color=%s,
                            year=%s,
                            updated_at=%s
                        WHERE id=%s
                    """, (
                        v.get("user_id"),
                        v.get("license_plate"),
                        v.get("make"),
                        v.get("model"),
                        v.get("color"),
                        v.get("year"),
                        datetime.now().strftime("%Y-%m-%d"),
                        v.get("id")
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO vehicles
                            (user_id, license_plate, make, model, color, year, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        v.get("user_id"),
                        v.get("license_plate"),
                        v.get("make"),
                        v.get("model"),
                        v.get("color"),
                        v.get("year"),
                        datetime.now().strftime("%Y-%m-%d"),
                        datetime.now().strftime("%Y-%m-%d")
                    ))

        conn.commit()
        return True

    except Error as e:
        print(f"DB Error: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()
