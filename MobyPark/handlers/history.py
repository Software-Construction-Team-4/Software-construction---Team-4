
import json
from MobyPark.DataAccesLayer.db_utils_parkingSessions import load_sessions_by_userID
from MobyPark.session_manager import get_session

def do_GET(self):
    token = self.headers.get("Authorization")
    session_user = get_session(token) if token else None

    if not token or not session_user:
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"Unauthorized: Invalid or missing session token")
        return

    target_user_id = self.path.replace("/history/", "").strip()

    if len(target_user_id) < 1: # get own history
        target_user_id = session_user.user_id
    elif target_user_id.isnumeric():
        target_user_id = int(target_user_id)
    else:
        self.send_response(400)
        self.send_headers("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write("Bad request: User IDs must be numerical")
        return

    # admin: history of other users
    if target_user_id != session_user.user_id and session_user.role.lower() != "admin":
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"Unauthorized: Cannot view other users' history")
        return

    sessions = load_sessions_by_userID(target_user_id)
    self.send_response(200)
    self.send_headers("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(
        json.dumps({
            "status": "Success",
            "history": sessions.to_json()
        }).encode("utf-8")
    )
