import uuid
import os
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from ..models.vault import PasswordEntry, VaultResponse
from ..core.crypto import CryptoService

router = APIRouter(prefix="/api/vault", tags=["vault"])

VAULT_DIR = "vaults"

def _get_vault_path(email: str) -> str:
    safe_email = email.replace("@", "_at_").replace(".", "_")
    return os.path.join(VAULT_DIR, f"{safe_email}.enc")

def _get_user_from_token(token: str) -> str:
    from ..core.session import _get_session
    session = _get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session.get("email")

def load_vault(email: str, password: str) -> dict:
    os.makedirs(VAULT_DIR, exist_ok=True)
    vault_path = _get_vault_path(email)
    if not os.path.exists(vault_path):
        return {"entries": []}
    crypto = CryptoService(password)
    with open(vault_path, "rb") as f:
        encrypted = f.read()
    try:
        return crypto.decrypt(encrypted)
    except:
        return {"entries": []}

def save_vault(email: str, password: str, data: dict):
    os.makedirs(VAULT_DIR, exist_ok=True)
    vault_path = _get_vault_path(email)
    crypto = CryptoService(password)
    encrypted = crypto.encrypt(data)
    with open(vault_path, "wb") as f:
        f.write(encrypted)

@router.get("", response_model=VaultResponse)
def get_vault(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    from ..core.session import _get_session
    session = _get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = session.get("email")
    vault = load_vault(email, email)
    return VaultResponse(entries=vault.get("entries", []))

@router.post("/entries")
def add_entry(entry: PasswordEntry, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    email = _get_user_from_token(token)
    entry.id = str(uuid.uuid4())
    vault = load_vault(email, email)
    vault.setdefault("entries", []).append(entry.model_dump())
    save_vault(email, email, vault)
    return entry

@router.put("/entries/{entry_id}")
def update_entry(entry_id: str, entry: PasswordEntry, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    email = _get_user_from_token(token)
    vault = load_vault(email, email)
    entries = vault.get("entries", [])
    for i, e in enumerate(entries):
        if e.get("id") == entry_id:
            entry.id = entry_id
            entries[i] = entry.model_dump()
            save_vault(email, email, vault)
            return entry
    raise HTTPException(status_code=404, detail="Entry not found")

@router.delete("/entries/{entry_id}")
def delete_entry(entry_id: str, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    email = _get_user_from_token(token)
    vault = load_vault(email, email)
    entries = vault.get("entries", [])
    vault["entries"] = [e for e in entries if e.get("id") != entry_id]
    save_vault(email, email, vault)
    return {"message": "Entry deleted"}

@router.get("/entries/search")
def search_entries(q: str, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    email = _get_user_from_token(token)
    vault = load_vault(email, email)
    query = q.lower()
    results = [e for e in vault.get("entries", []) if query in e.get("title", "").lower() or query in e.get("username", "").lower()]
    return VaultResponse(entries=results)
