import hashlib
import secrets
import json
import os

SESSION_FILE = "session.json"
SESSION_TIMEOUT = 900

class AuthService:
    def __init__(self, master_password: str):
        self.master_hash = self._hash_password(master_password)
        self.session_token = None

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_master_password(self, password: str) -> bool:
        return self._hash_password(password) == self.master_hash

    def create_session(self):
        self.session_token = secrets.token_urlsafe(32)
        session_data = {
            "token": self.session_token,
            "expires_at": SESSION_TIMEOUT
        }
        with open(SESSION_FILE, "w") as f:
            json.dump(session_data, f)
        return self.session_token

    def verify_session(self, token: str) -> bool:
        if not os.path.exists(SESSION_FILE):
            return False
        try:
            with open(SESSION_FILE, "r") as f:
                session_data = json.load(f)
            return session_data.get("token") == token
        except:
            return False

    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.session_token = None
