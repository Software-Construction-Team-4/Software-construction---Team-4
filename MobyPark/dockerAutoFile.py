import mysql.connector
from datetime import datetime, date
from DataAccesLayer.db_utils_reservations import pending_to_expired
from DataAccesLayer.db_utils_parkingSessions import create_parking_sessions_from_expired_reservations


def run():
    expired_reservations = pending_to_expired()
    create_parking_sessions_from_expired_reservations(expired_reservations)

    with open("/var/log/cron.log", "a") as f:
        f.write(f"[{datetime.now()}] 12-hour task ran\n")
        # Logger.log("Ran 12-hour task.")

if __name__ == "__main__":
    run()
