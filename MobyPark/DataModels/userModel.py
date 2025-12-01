from datetime import date

class userModel:
    def __init__(self, id : int, username : str, password : str, name : str, email : str, phone : str, role : str,
                 created_at : str, birth_year : date, active : date):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role
        self.created_at = created_at
        self.birth_year = birth_year
        self.active = active

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at,
            "birth_year": self.birth_year,
            "active": self.active
        }