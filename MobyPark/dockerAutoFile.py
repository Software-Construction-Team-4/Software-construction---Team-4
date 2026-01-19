import mysql.connector
from datetime import datetime, date
from LogicLayer.reservationsLogic import process_missed_sessions

def get_db_connection():
    return mysql.connector.connect(
        host="145.24.237.71",
        port=8001,
        user="vscode",
        password="StrongPassword123!",
        database="mobypark"
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
    process_missed_sessions(date.today())
    pending_to_expired()

    with open("/var/log/cron.log", "a") as f:
        f.write(f"[{datetime.now()}] 12-hour task ran\n")
        # Logger.log("Ran 12-hour task.")

if __name__ == "__main__":
    run()
