import json
import hashlib
import uuid
from datetime import date
from DataAccesLayer.db_utils_users import load_users, save_user, update_user_data
from session_manager import add_session, remove_session, get_session
from DataModels.userModel import userModel

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

        users = load_users()

        for user in users:
            if username == user.username:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Username already taken")
                return

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

            users = load_users()
            for user in users:
                if user.username == username:
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
        users = load_users()

        foundUser = next((u for u in users if str(u.id) == str(data["id"])), None)
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

