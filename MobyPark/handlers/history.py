import json
# from DataAccesLayer.db_utils_parkingSessions import load_sessions_by_userID
from LogicLayer.sessionLogic import load_sessions_for_user
from session_manager import get_session

def do_GET(self):
    token = self.headers.get("Authorization")
    session_user = get_session(token) if token else None

    if not token or not session_user:
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"Unauthorized: Invalid or missing session token")
        return

    path = self.path.split('/')
    target_user_id = session_user.get("user_id") # default to the user performing the request

    if len(path) >= 3 and len(path[2].strip()) > 0: # admin: a user ID has been provided
        uid = path[2]
        if uid.isnumeric():
            target_user_id = int(uid)
        else:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"Bad request: User IDs must be numerical")
            return

    # admin: history of other users
    if target_user_id != session_user.get("user_id") and session_user.get("role").lower() != "admin":
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"Unauthorized: Cannot view other users' history")
        return

    sessions = load_sessions_for_user(target_user_id)
    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(
        json.dumps({
            "status": "Success",
            "history": [
                {
                    "id": session.id,
                    "parking_lot_id": session.parking_lot_id,
                    "session": session.session,
                    "user_id": session.user_id,
                    "licenseplate": session.licenseplate,
                    "started": session.started.isoformat(),
                    "stopped": session.stopped.isoformat(),
                    "duration_minutes": session.duration_minutes,
                    "cost": float(session.cost),
                    "payment_status": session.payment_status
                }
                for session in sessions
            ]
        }).encode("utf-8")
    )
