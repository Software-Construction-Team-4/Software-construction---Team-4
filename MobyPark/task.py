# MobyPark/task.py
from datetime import datetime

def run():
    with open("/var/log/cron.log", "a") as f:
        f.write(f"[{datetime.now()}] 12-hour task ran\n")

if __name__ == "__main__":
    run()
