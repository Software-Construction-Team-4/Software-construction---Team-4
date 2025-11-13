from typing import Optional
import mysql.connector
from datetime import datetime

# TODO place this in a gitignored .env file
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="vscode",
    password="StrongPassword123!!",
    database="mobypark"
)
cursor = db.cursor()

# user_id, license_plate, make, model, color, year, created_at, updated_at
class Vehicle:
    TABLE: str = "vehicles"
    DATE_FORMAT: str = "%Y-%m-%d"

    def __init__(self, id: int, user_id: int, license_plate: str, make: str, model: str, color: str, year: int,
                 created_at: str = datetime.now().strftime(DATE_FORMAT), updated_at: str = datetime.now().strftime(DATE_FORMAT)) -> 'Vehicle':
        self.id = id
        self.user_id = user_id
        self.license_plate = license_plate
        self.make = make
        self.model = model
        self.color = color
        self.year = year
        self.created_at = created_at
        self.updated_at = updated_at

    def update(self) -> 'Vehicle':
        vehicle_exists: bool = cursor.fetchone(f"SELECT id FROM {Vehicle.TABLE} WHERE id = %s", (self.id,)) is not None
        now = datetime.now().strftime(Vehicle.DATE_FORMAT)

        if (vehicle_exists):
            cursor.execute(f'''
                            UPDATE {Vehicle.TABLE} SET
                                user_id = %s, license_plate = %s, make = %s, model = %s, color = %s, year = %s, created_at = %s, updated_at = %s
                            WHERE id = %s
                           ''', (self.user_id, self.license_plate, self.make, self.model, self.color, self.year, self.created_at, now, self.id))
        else:
            cursor.execute(f'''
                            INSERT INTO {Vehicle.TABLE}
                                (user_id, license_plate, make, model, color, year, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                           ''', (self.user_id, self.license_plate, self.make, self.model, self.color, self.year, now, now))

        db.commit()
        return Vehicle.get_by_id(cursor.lastrowid) # get the updated vehicle, now with an id if newly created

    def delete(self) -> None:
        cursor.execute(f"DELETE FROM {Vehicle.TABLE} WHERE id = %s", (self.id,))
        db.commit()

    @staticmethod
    def get_by_id(id: int) -> Optional['Vehicle']:
        result = cursor.fetchone(f"SELECT * FROM {Vehicle.TABLE} WHERE id = %s", (id,))
        return (result is not None) and Vehicle(*result) or None

    @staticmethod
    def get_all_vehicles() -> list['Vehicle']:
        result = cursor.fetchall(f"SELECT * FROM {Vehicle.TABLE}")
        return [Vehicle(*vehicle) for vehicle in result]

    @staticmethod
    def get_all_user_vehicles(user_id: int) -> list['Vehicle']:
        result = cursor.fetchall(f"SELECT * FROM {Vehicle.TABLE} WHERE user_id = %s", (user_id,))
        return [Vehicle(*vehicle) for vehicle in result]
