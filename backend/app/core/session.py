import secrets
import os
import json

SESSION_DIR = "sessions"

def _create_session(email: str):
    os.makedirs(SESSION_DIR, exist_ok=True)
    token = secrets.token_urlsafe(32)
    safe_email = email.replace('@', '_at_').replace('.', '_')
    session_file = os.path.join(SESSION_DIR, f"{safe_email}.json")
    with open(session_file, "w") as f:
        json.dump({"token": token, "email": email}, f)
    return token

def _get_session(token: str):
    if not os.path.exists(SESSION_DIR):
        return None
    try:
        for filename in os.listdir(SESSION_DIR):
            if filename.endswith(".json"):
                session_file = os.path.join(SESSION_DIR, filename)
                with open(session_file, "r") as f:
                    data = json.load(f)
                    if data.get("token") == token:
                        return data
    except:
        pass
    return None

def _delete_session(email: str):
    safe_email = email.replace('@', '_at_').replace('.', '_')
    session_file = os.path.join(SESSION_DIR, f"{safe_email}.json")
    if os.path.exists(session_file):
        os.remove(session_file)
