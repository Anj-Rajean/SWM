from pydantic import BaseModel
from typing import Optional

class PasswordEntry(BaseModel):
    id: Optional[str] = None
    title: str
    username: str
    password: str
    url: Optional[str] = None
    notes: Optional[str] = None

class VaultResponse(BaseModel):
    entries: list[PasswordEntry]
