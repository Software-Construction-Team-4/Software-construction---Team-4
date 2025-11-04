import json
import hashlib
import uuid
from MobyPark.db.users import User
from storage_utils import load_json, save_user_data # pyright: ignore[reportUnknownVariableType]
from session_manager import add_session, remove_session, get_session # pyright: ignore[reportUnknownVariableType]

def do_POST(self):
    if self.path == "/register":
            data  = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
            username = data.get("username")
            password = data.get("password")
            name = data.get("name")
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            existing_user = User.get_by_username(username)
            if existing_user is not None:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Username already taken")
                return

            new_user = User(-1, username, hashed_password, name)
            new_user.update()
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
            user = User.get_by_username(username)
            if (user is None):
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"User not found")
            elif (user.password == hashed_password):
                token = str(uuid.uuid4())
                add_session(token, user)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "User logged in", "session_token": token}).encode('utf-8'))
            else:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b"Invalid credentials")

def do_PUT(self):
    if self.path == "/profile":
        token = self.headers.get('Authorization')
        if not token or not get_session(token):
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Invalid or missing session token")
            return

        session_user = get_session(token)
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", -1))))
        new_username = data.get("username")
        if User.get_by_username(new_username) is not None:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Username is taken")
            return

        session_user.username = data.get("username")

        if data.get("password"):
            session_user.password = hashlib.md5(data["password"].encode()).hexdigest()

        session_user.update()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b"User updated successfully")


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


def do_DELETE(self):
    return
