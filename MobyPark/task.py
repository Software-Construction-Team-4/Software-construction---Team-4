from datetime import datetime
from DataAccesLayer.db_utils_reservations import cehck_and_update_reservation_status_12_hours

def run():
    cehck_and_update_reservation_status_12_hours()
    
    with open("/var/log/cron.log", "a") as f:
        f.write(f"[{datetime.now()}] 12-hour task ran\n")

if __name__ == "__main__":
    run()
