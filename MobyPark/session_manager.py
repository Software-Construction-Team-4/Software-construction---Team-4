sessions = {}

def add_session(token, user):
    sessions[token] = {
        "username": user.username,
        "user_id": user.id,
        "role": user.role
    }

def remove_session(token):
    """Remove an active session by token."""
    return sessions.pop(token, None)

def get_session(token):
    """Retrieve a session dictionary by token."""
    return sessions.get(token)
