from typing import Optional
import mysql.connector
from enum import StrEnum
from datetime import datetime

db = mysql.connector.connect(host="localhost", user="root", password="admin", database="mobypark")
cursor = db.cursor()

class UserRole(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"

class User:
    CREATION_DATE_FORMAT: str = "%Y-%m-%d"

    def __init__(self, id: int, username: str, password: str, name: str, email: Optional[str] = None, phone: Optional[str] = None, role: Optional[UserRole] = UserRole.USER,
                 created_at: str = datetime.now().strftime(CREATION_DATE_FORMAT), birth_year: Optional[int] = None, active: bool = True) -> 'User':
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role
        self.created_at = datetime.strptime(created_at, User.CREATION_DATE_FORMAT)
        self.birth_year = birth_year
        self.active = active

    @staticmethod
    def get_by_id(id: int) -> Optional['User']:
        result = cursor.fetchone("SELECT * FROM users WHERE id = ?", (id,))
        return (result is not None) and User(*result) or None

    @staticmethod
    def get_by_username(username: str) -> Optional['User']:
        result = cursor.fetchone("SELECT * FROM users WHERE LOWER(username) = ?", (username.lower(),))
        return (result is not None) and User(*result) or None
