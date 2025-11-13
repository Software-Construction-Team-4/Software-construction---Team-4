from typing import Optional
import mysql.connector
from enum import StrEnum
from datetime import datetime

db = mysql.connector.connect(host="145.24.237.71", port = "8001",user="root", password="admin", database="mobypark")
cursor = db.cursor()

class UserRole(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"

class User:
    TABLE = "users"
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

    def update(self) -> 'User':
        result = cursor.execute(f'''
                                 INSERT INTO {User.TABLE} (username, password, name, email, phone, role, created_at, birth_year, active)
                                 VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                 ON DUPLICATE KEY UPDATE
                                 ''',
                                 (self.username, self.password, self.name, self.email, self.phone, self.role, self.created_at, self.birth_year, self.active)
                                 )
        return User(*result)

    @staticmethod
    def get_by_id(id: int) -> Optional['User']:
        result = cursor.fetchone(f"SELECT * FROM {User.TABLE} WHERE id = %s", (id,))
        return (result is not None) and User(*result) or None

    @staticmethod
    def get_by_username(username: str) -> Optional['User']:
        result = cursor.fetchone(f"SELECT * FROM {User.TABLE} WHERE LOWER(username) = %s", (username.lower(),))
        return (result is not None) and User(*result) or None

    @staticmethod
    def get_all_users() -> list['User']:
        result = cursor.fetchall(f"SELECT * FROM {User.TABLE}")
        return [User(*user) for user in result]
