import uuid
from typing import Optional

class PasswordEntry:
    def __init__(
        self,
        id: str = None,
        title: str = "",
        username: str = "",
        password: str = "",
        url: Optional[str] = None,
        notes: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.username = username
        self.password = password
        self.url = url
        self.notes = notes
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "username": self.username,
            "password": self.password,
            "url": self.url,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PasswordEntry":
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            username=data.get("username", ""),
            password=data.get("password", ""),
            url=data.get("url"),
            notes=data.get("notes")
        )
    
    def is_valid(self) -> bool:
        return bool(self.title and self.username and self.password)


class Vault:
    def __init__(self, entries: list = None):
        self.entries = entries or []
    
    def add_entry(self, entry: PasswordEntry):
        self.entries.append(entry)
    
    def update_entry(self, entry_id: str, entry: PasswordEntry):
        for i, e in enumerate(self.entries):
            if e.id == entry_id:
                self.entries[i] = entry
                return True
        return False
    
    def delete_entry(self, entry_id: str) -> bool:
        initial_count = len(self.entries)
        self.entries = [e for e in self.entries if e.id != entry_id]
        return len(self.entries) < initial_count
    
    def search(self, query: str) -> list:
        query = query.lower()
        return [
            e for e in self.entries
            if query in e.title.lower() or query in e.username.lower()
        ]
    
    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}
    
    @classmethod
    def from_dict(cls, data: dict) -> "Vault":
        entries = [PasswordEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(entries)
