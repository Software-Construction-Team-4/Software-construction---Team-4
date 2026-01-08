import json
import hashlib
import uuid
from datetime import date
from DataAccesLayer.db_utils_users import load_users, save_user, update_user_data, get_user_by_username, get_user_by_email, get_user_by_phone, get_user_by_id
from session_manager import add_session, remove_session, get_session
from DataModels.userModel import userModel
from LogicLayer.userLogic import UserLogic

def do_POST(self):
    if self.path == "/register":
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
        username = data.get("username")
        password = data.get("password")
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        birth_year = data.get("birth_year")

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        passResult = UserLogic.CheckPassword(password)
        nameResult = UserLogic.CheckName(name)
        emailResult = UserLogic.CheckEmail(email)
        phoneResult = UserLogic.CheckPhone(phone)

        passErrors = {
            0: b"Password must be at least 8 characters long",
            1: b"Password must contain at least one uppercase character",
            2: b"Password must contain at least one lowercase character",
            3: b"Password must contain at least one number",
            4: b"Password must contain at least one special character"
        }

        nameErrors = {
            0: b"You must give your first and last name",
            1: b"Name can't contain number or special character"
        }

        emailErrors = {
            0: b"Email can't contain a space in it",
            1: b"Email must contain only one '@'",
            2: b"You must have a name before the '@'",
            3: b"your email is either missing a dot or its domain",
            4: b"Password must contain at least one special character"
        }

        if passResult in passErrors:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(passErrors[passResult])
            return
        
        if nameResult in nameErrors:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(nameErrors[nameResult])
            return
        
        if emailResult in emailErrors:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(emailErrors[emailResult])
            return

        if phoneResult == 0:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Invalid phone number. Must contain only digits. Length must be 9 digits if '+' isn't provided, or 12 digits including '+' if country code is included.")
            return

        
        if get_user_by_username(username):
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Username already taken")
            return
        
        if get_user_by_email(email):
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Email is already in use")
            return
        
        if get_user_by_phone(phone):
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Phone number is already in use")
            return

        if len(phone) == 9:
            phone = "+310" + phone
            
        new_user = userModel(
            id=None,
            username=username,
            password=hashed_password,
            name=name,
            email=email,
            phone=phone,
            role="USER",
            created_at=date.today().isoformat(),
            birth_year=birth_year,
            active=True
        )

        save_user(new_user)

        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b"User created")


    elif self.path == "/login":
            # find_duplicate_users()
            # deactivate_duplicate_users()
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            username = data.get("username")
            password = data.get("password")
            if not username or not password:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Missing credentials")
                return
            hashed_password = hashlib.md5(password.encode()).hexdigest()

            user = get_user_by_username(username)
            if user:
                if user.password == hashed_password:
                    token = str(uuid.uuid4())
                    add_session(token, user)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"message": "User logged in", "session_token": token, "user_id": user.id}).encode('utf-8'))
                    return
                else:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b"Invalid credentials")
                    return
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"User not found")


def do_PUT(self):
    if self.path == "/profile":
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        # session_user = get_session(token)
        content_length = int(self.headers.get("Content-Length", -1))
        if content_length <= 0:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Empty request body")
            return

        data = json.loads(self.rfile.read(content_length))

        foundUser = get_user_by_id(data["id"])
        if foundUser is None:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"User not found")
            return
        
        if foundUser.id != get_session(token)['user_id'] and get_session(token)['role'] != "ADMIN":
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"You don't have authority to update this user")
            return
        
        if "password" in data:
            passResult = UserLogic.CheckPassword(data["password"])
            passErrors = {
                0: b"Password must be at least 8 characters long",
                1: b"Password must contain at least one uppercase character",
                2: b"Password must contain at least one lowercase character",
                3: b"Password must contain at least one number",
                4: b"Password must contain at least one special character"
            }
            if passResult in passErrors:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(passErrors[passResult])
                return

        if "name" in data:
            nameResult = UserLogic.CheckName(data["name"])
            nameErrors = {
                0: b"You must give your first and last name",
                1: b"Name can't contain number or special character"
            }
            if nameResult in nameErrors:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(nameErrors[nameResult])
                return

        if "email" in data:
            emailResult = UserLogic.CheckEmail(data["email"])
            emailErrors = {
                0: b"Email can't contain a space in it",
                1: b"Email must contain only one '@'",
                2: b"You must have a name before the '@'",
                3: b"Your email is missing a dot or domain"
            }
            if emailResult in emailErrors:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(emailErrors[emailResult])
                return

        if "phone" in data:
            phoneResult = UserLogic.CheckPhone(data["phone"])
            if phoneResult == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(
                    b"Invalid phone number. Must contain only digits. Length must be 9 digits without '+' or 12 digits with it."
                )
                return

        updatable_fields = [
            "username",
            "password",
            "name",
            "email",
            "phone",
            "birth_year",
            "active"
        ]

        for field in updatable_fields:
            if field in data:
                value = data[field]
                if field == "password":
                    value = hashlib.md5(data[field].encode()).hexdigest()

                setattr(foundUser, field, value)

        update_user_data(foundUser)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b"User updated successfully")
        return


def do_GET(self):
    if self.path == "/profile":
            token = self.headers.get('Authorization')
            if not token or not get_session(token):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Unauthorized: Invalid or missing session token")
                return
            session_user = get_session(token)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(session_user).encode('utf-8'))


    elif self.path == "/logout":
            token = self.headers.get('Authorization')
            if token and get_session(token):
                remove_session(token)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"User logged out")
                return
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Invalid session token")
    return

