import os
from app.core.crypto import CryptoService, VaultStorage
from app.models.vault import PasswordEntry, Vault


class VaultController:
    def __init__(self, master_password: str = None):
        self.crypto = None
        self.storage = None
        self.vault = None
        self.is_authenticated = False
        
        if master_password:
            self._initialize(master_password)
    
    def _initialize(self, master_password: str):
        self.crypto = CryptoService(master_password)
        self.storage = VaultStorage(self.crypto)
        
        if self.storage.exists():
            data = self.storage.load()
            self.vault = Vault.from_dict(data)
            self.is_authenticated = True
        else:
            self.vault = Vault()
            self.storage.save(self.vault.to_dict())
            self.is_authenticated = True
    
    def authenticate(self, master_password: str) -> bool:
        self.crypto = CryptoService(master_password)
        self.storage = VaultStorage(self.crypto)
        
        if not self.storage.exists():
            if len(master_password) < 6:
                return False
            self.vault = Vault()
            self.storage.save(self.vault.to_dict())
            self.is_authenticated = True
            return True
        
        data = self.storage.load()
        if data.get("entries") is None:
            return False
        
        self.vault = Vault.from_dict(data)
        self.is_authenticated = True
        return True
    
    def is_new_vault(self) -> bool:
        return not os.path.exists(VaultStorage.VAULT_FILE)
    
    def add_entry(self, title: str, username: str, password: str, url: str = None, notes: str = None) -> PasswordEntry:
        if not self.is_authenticated:
            raise Exception("Not authenticated")
        
        entry = PasswordEntry(
            title=title,
            username=username,
            password=password,
            url=url,
            notes=notes
        )
        
        self.vault.add_entry(entry)
        self._save()
        return entry
    
    def update_entry(self, entry_id: str, title: str, username: str, password: str, url: str = None, notes: str = None) -> bool:
        if not self.is_authenticated:
            raise Exception("Not authenticated")
        
        entry = PasswordEntry(
            id=entry_id,
            title=title,
            username=username,
            password=password,
            url=url,
            notes=notes
        )
        
        result = self.vault.update_entry(entry_id, entry)
        self._save()
        return result
    
    def delete_entry(self, entry_id: str) -> bool:
        if not self.is_authenticated:
            raise Exception("Not authenticated")
        
        result = self.vault.delete_entry(entry_id)
        self._save()
        return result
    
    def search(self, query: str) -> list:
        if not self.is_authenticated:
            raise Exception("Not authenticated")
        
        return self.vault.search(query)
    
    def get_all_entries(self) -> list:
        if not self.is_authenticated:
            raise Exception("Not authenticated")
        
        return self.vault.entries
    
    def _save(self):
        if self.storage and self.vault:
            self.storage.save(self.vault.to_dict())
    
    def logout(self):
        self.crypto = None
        self.storage = None
        self.vault = None
        self.is_authenticated = False
    
    @staticmethod
    def storage_exists() -> bool:
        return os.path.exists(VaultStorage.VAULT_FILE)

