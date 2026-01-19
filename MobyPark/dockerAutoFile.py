import mysql.connector
from datetime import datetime
from DataAccesLayer.db_utils_reservations import create_missed_parking_sessions

from environment import Environment
def get_db_connection():
    return mysql.connector.connect(
        host=Environment.get_var("DB_HOST"),
        port=int(Environment.get_var("DB_PORT")),
        user=Environment.get_var("DB_USER"),
        password=Environment.get_var("DB_PASSWORD"),
        database=Environment.get_var("DB_NAME")
    )

def pending_to_expired():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE reservations
            SET status = 'expired'
            WHERE status = 'pending'
            AND end_time < NOW()
        """)
        conn.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        conn.close()

def run():
    create_missed_parking_sessions()
    pending_to_expired()

    with open("/var/log/cron.log", "a") as f:
        f.write(f"[{datetime.now()}] 12-hour task ran\n")
        Logger.log("Ran 12-hour task.")

if __name__ == "__main__":
    run()
