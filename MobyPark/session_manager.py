sessions = {}

def add_session(token, user):
    """
    Store a session for a logged-in user.
    The `user` dict must include at least: username and user_id.
    """
    # Ensure we store only safe fields
    sessions[token] = {
        "username": user.get("username"),
        "user_id": user.get("id") or user.get("user_id")
    }

def remove_session(token):
    """Remove an active session by token."""
    return sessions.pop(token, None)

def get_session(token):
    """Retrieve a session dictionary by token."""
    return sessions.get(token)
