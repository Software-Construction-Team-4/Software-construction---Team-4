class VehicleModel:
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, id, user_id, license_plate, make, model, color, year, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.license_plate = license_plate
        self.make = make
        self.model = model
        self.color = color
        self.year = year
        self.created_at = created_at
        self.updated_at = updated_at

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "license_plate": self.license_plate,
            "make": self.make,
            "model": self.model,
            "color": self.color,
            "year": self.year,
            "created_at": self.created_at.strftime(self.DATE_FORMAT) if self.created_at else None,
            "updated_at": self.updated_at.strftime(self.DATE_FORMAT) if self.updated_at else None,
        }
