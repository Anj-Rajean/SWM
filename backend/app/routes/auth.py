import secrets
import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

SESSION_DIR = "sessions"

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    message: str
    token: str
    user: dict

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
    for filename in os.listdir(SESSION_DIR):
        if filename.endswith(".json"):
            session_file = os.path.join(SESSION_DIR, filename)
            with open(session_file, "r") as f:
                data = json.load(f)
                if data.get("token") == token:
                    return data
    return None

def _delete_session(email: str):
    safe_email = email.replace('@', '_at_').replace('.', '_')
    session_file = os.path.join(SESSION_DIR, f"{safe_email}.json")
    if os.path.exists(session_file):
        os.remove(session_file)

@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest):
    from ..core.database import create_user, get_user
    
    try:
        existing = get_user(request.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        success = create_user(request.email, request.password)
        if success:
            token = _create_session(request.email)
            return AuthResponse(message="Account created", token=token, user={"email": request.email})
        raise HTTPException(status_code=500, detail="Failed to create account")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):
    from ..core.database import verify_user, get_user
    
    try:
        if not verify_user(request.email, request.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = get_user(request.email)
        if user:
            _delete_session(request.email)
            token = _create_session(request.email)
            return AuthResponse(message="Login successful", token=token, user={"email": request.email})
        raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
def logout(token: str):
    from ..core.session import _get_session, _delete_session
    session = _get_session(token)
    if session:
        _delete_session(session.get("email"))
    return {"message": "Logged out"}

@router.get("/verify")
def verify_token(token: str):
    from ..core.session import _get_session
    session = _get_session(token)
    if session:
        return {"valid": True, "email": session.get("email")}
    return {"valid": False}
