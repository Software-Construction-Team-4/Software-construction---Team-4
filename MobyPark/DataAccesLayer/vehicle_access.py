import datetime
from typing import Optional
import mysql.connector

from DataModels.vehicle_model import VehicleModel

# TODO place this in a gitignored .env file
db = mysql.connector.connect(
    host="145.24.237.71",
    port=8001,
    user="vscode",
    password="StrongPassword123!",
    database="mobypark"
)

# db = mysql.connector.connect(
#         host="localhost",
#         port=3306,
#         user="root",
#         password="Kikkervis66!",
#         database="mobypark"
#     )
cursor = db.cursor()


class UserAlreadyHasVehicleError(Exception):
    """Raised when a user tries to create more than one vehicle."""
    pass


class VehicleAccess:
    TABLE: str = "vehicles"

    @staticmethod
    def update(vehicle: VehicleModel) -> 'VehicleModel':
        """
        Update an existing vehicle in the database and return the refreshed model.
        """
        now = datetime.datetime.now().strftime(VehicleModel.DATE_FORMAT)

        cursor.execute(f"""
            UPDATE {VehicleAccess.TABLE}
            SET
                user_id = %s,
                license_plate = %s,
                make = %s,
                model = %s,
                color = %s,
                year = %s,
                updated_at = %s
            WHERE id = %s
        """, (
            vehicle.user_id,
            vehicle.license_plate,
            vehicle.make,
            vehicle.model,
            vehicle.color,
            vehicle.year,
            now,
            vehicle.id
        ))

        db.commit()
        return VehicleAccess.get_by_id(vehicle.id)

    @staticmethod
    def delete(vehicle: VehicleModel) -> None:
        cursor.execute(f"DELETE FROM {VehicleAccess.TABLE} WHERE id = %s", (vehicle.id,))
        db.commit()

    @staticmethod
    def get_by_id(id: int) -> Optional['VehicleModel']:
        cursor.execute(f"SELECT * FROM {VehicleAccess.TABLE} WHERE id = %s", (id,))
        result = cursor.fetchone()
        return (result is not None) and VehicleModel(*result) or None

    @staticmethod
    def get_all_vehicles() -> list['VehicleModel']:
        cursor.execute(f"SELECT * FROM {VehicleAccess.TABLE}")
        result = cursor.fetchall()
        return [VehicleModel(*vehicle) for vehicle in result]

    @staticmethod
    def get_all_user_vehicles(user_id: int) -> list['VehicleModel']:
        cursor.execute(f"SELECT * FROM {VehicleAccess.TABLE} WHERE user_id = %s", (user_id,))
        result = cursor.fetchall()
        return [VehicleModel(*vehicle) for vehicle in result]

    @staticmethod
    def user_has_vehicle(user_id: int) -> bool:
        """
        Check if the given user already has at least one vehicle.
        """
        cursor.execute(
            f"SELECT id FROM {VehicleAccess.TABLE} WHERE user_id = %s LIMIT 1",
            (user_id,)
        )
        return cursor.fetchone() is not None

    @staticmethod
    def create(vehicle: VehicleModel) -> Optional['VehicleModel']:

        if VehicleAccess.user_has_vehicle(vehicle.user_id):
            raise UserAlreadyHasVehicleError("User already has a vehicle")

        now = datetime.datetime.now().strftime(VehicleModel.DATE_FORMAT)

        cursor.execute(f"""
            INSERT INTO {VehicleAccess.TABLE}
                (user_id, license_plate, make, model, color, year, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            vehicle.user_id, vehicle.license_plate, vehicle.make,
            vehicle.model, vehicle.color, vehicle.year,
            now, None
        ))

        db.commit()
        new_id = cursor.lastrowid

        cursor.execute(f"SELECT * FROM {VehicleAccess.TABLE} WHERE id = %s", (new_id,))
        row = cursor.fetchone()
        if row:
            return VehicleModel(
                id=row[0],
                user_id=row[1],
                license_plate=row[2],
                make=row[3],
                model=row[4],
                color=row[5],
                year=row[6],
                created_at=row[7],
                updated_at=row[8]
            )
        return None
