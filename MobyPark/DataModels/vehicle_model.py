# user_id, license_plate, make, model, color, year, created_at, updated_at
from datetime import datetime
from typing import Union

class VehicleModel:
    DATE_FORMAT: str = "%Y-%m-%d"

    def __init__(self, id: int, user_id: int, license_plate: str, make: str, model: str, color: str, year: int,
                 created_at: Union[str, datetime] = datetime.now(), updated_at: Union[str, datetime] = datetime.now()) -> 'VehicleModel':
        self.id = id
        self.user_id = user_id
        self.license_plate = license_plate
        self.make = make
        self.model = model
        self.color = color
        self.year = year

        self.created_at = created_at
        if (isinstance(self.created_at, str)):
            self.created_at = datetime.strptime(self.created_at, VehicleModel.DATE_FORMAT)

        self.updated_at = updated_at
        if (isinstance(self.updated_at, str)):
            self.updated_at = datetime.strptime(self.updated_at, VehicleModel.DATE_FORMAT)
