# ErgoSecure Desktop - Documentation Technique

## Presentation

ErgoSecure est une application desktop de gestion de mots de passe securisee, build avec Python et CustomTkinter. Elle offre une interface graphique moderne pour stocker et gerer vos mots de passe de maniere securisee.

## Caracteristiques

- **Stockage local**: Tous les donnees sont stockees dans un fichier local chiffre
- **Chiffrement AES-256-CBC**: Algorithme de chiffrement robuste avec derive de cle PBKDF2
- **Architecture MVC**: Separation claire des responsabilites
- **Sans connexion**: Fonctionne entierement hors ligne, pas de dependance externe
- **Generation de mots de passe**: Generateur automatique de mots de passe securises

---

## Structure du Projet

```
desktop/
├── main.py                    # Point d'entree de l'application
├── requirements.txt            # Dependencies Python
└── app/
    ├── core/
    │   └── crypto.py          # Services de chiffrement et stockage
    ├── models/
    │   └── vault.py          # Modeles de donnees (PasswordEntry, Vault)
    ├── views/
    │   └── gui.py            # Interfaces graphiques (LoginView, DashboardView)
    └── controllers/
        └── vault.py          # Logique metier (VaultController)
```

---

## Installation

### Dependencies

```bash
pip install customtkinter==5.2.2 cryptography==42.0.0
```

### Lancement

```bash
cd desktop
python main.py
```

---

## Detail des Fichiers

### 1. app/core/crypto.py - Services de Chiffrement

Ce fichier contient les classes `CryptoService` et `VaultStorage` pour le chiffrement et le stockage.

```python
# app/core/crypto.py
import os
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoService:
    """Service de chiffrement AES-256-CBC"""
    
    def __init__(self, password: str, salt: bytes = None):
        self.password = password
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key(password)

    def _derive_key(self, password: str) -> bytes:
        """Derive une cle de 32 octets depuis le mot de passe"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt(self, data: dict) -> bytes:
        """Chiffre un dictionnaire en bytes"""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        json_data = json.dumps(data).encode()
        padding = 16 - len(json_data) % 16
        json_data += bytes([padding] * padding)
        
        ciphertext = encryptor.update(json_data) + encryptor.finalize()
        return base64.b64encode(iv + self.salt + ciphertext)

    def decrypt(self, encrypted_data: bytes) -> dict:
        """Dechiffre des bytes en dictionnaire"""
        data = base64.b64decode(encrypted_data)
        iv = data[:16]
        salt = data[16:32]
        ciphertext = data[32:]
        
        temp_crypto = CryptoService(self.password, salt)
        
        cipher = Cipher(algorithms.AES(temp_crypto.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        padding = plaintext[-1]
        plaintext = plaintext[:-padding]
        
        return json.loads(plaintext.decode())


class VaultStorage:
    """Gestion du stockage local dans vault.enc"""
    VAULT_FILE = "vault.enc"
    
    def __init__(self, crypto_service: CryptoService):
        self.crypto = crypto_service
    
    def save(self, data: dict):
        """Sauvegarde les donnees chiffrees"""
        encrypted = self.crypto.encrypt(data)
        with open(self.VAULT_FILE, "wb") as f:
            f.write(encrypted)
    
    def load(self) -> dict:
        """Charge et dechiffre les donnees"""
        if not os.path.exists(self.VAULT_FILE):
            return {"entries": []}
        
        with open(self.VAULT_FILE, "rb") as f:
            encrypted = f.read()
        
        try:
            return self.crypto.decrypt(encrypted)
        except:
            return {"entries": []}
    
    def exists(self) -> bool:
        """Verifie si le fichier de coffre existe"""
        return os.path.exists(self.VAULT_FILE)
```

**Explication:**
- `CryptoService`: Utilise PBKDF2 pour deriver une cle depuis le mot de passe, puis chiffre avec AES-256-CBC
- `VaultStorage`: Encapsule les operations de lecture/ecriture du fichier chiffre

---

### 2. app/models/vault.py - Modeles de Donnees

Definit les structures de donnees pour les entrees et le coffre.

```python
# app/models/vault.py
import uuid
from typing import Optional


class PasswordEntry:
    """Represent une entree de mot de passe"""
    
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
        """Convertit en dictionnaire"""
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
        """Cree depuis un dictionnaire"""
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            username=data.get("username", ""),
            password=data.get("password", ""),
            url=data.get("url"),
            notes=data.get("notes")
        )
    
    def is_valid(self) -> bool:
        """Verifie si les champs requis sont remplis"""
        return bool(self.title and self.username and self.password)


class Vault:
    """Gestionnaire de la collection d'entrees"""
    
    def __init__(self, entries: list = None):
        self.entries = entries or []
    
    def add_entry(self, entry: PasswordEntry):
        self.entries.append(entry)
    
    def update_entry(self, entry_id: str, entry: PasswordEntry) -> bool:
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
```

**Explication:**
- `PasswordEntry`: Represente une entree (titre, username, password, url, notes)
- `Vault`: Collection d'entrees avec methodes CRUD et recherche

---

### 3. app/controllers/vault.py - Controleur

Gere la logique metier et fait le lien entre modeles et vue.

```python
# app/controllers/vault.py
import os
from app.core.crypto import CryptoService, VaultStorage
from app.models.vault import PasswordEntry, Vault


class VaultController:
    """Controleur principal de l'application"""
    
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
        """Authentifie l'utilisateur"""
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
    
    def add_entry(self, title: str, username: str, password: str, url: str = None, notes: str = None):
        """Ajoute une nouvelle entree"""
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
    
    def update_entry(self, entry_id: str, title: str, username: str, password: str, url: str = None, notes: str = None):
        """Met a jour une entree existante"""
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
    
    def delete_entry(self, entry_id: str):
        """Supprime une entree"""
        result = self.vault.delete_entry(entry_id)
        self._save()
        return result
    
    def search(self, query: str):
        """Recherche des entrees"""
        return self.vault.search(query)
    
    def get_all_entries(self) -> list:
        """Retourne toutes les entrees"""
        return self.vault.entries
    
    def _save(self):
        if self.storage and self.vault:
            self.storage.save(self.vault.to_dict())
    
    def logout(self):
        """Deconnecte l'utilisateur"""
        self.crypto = None
        self.storage = None
        self.vault = None
        self.is_authenticated = False
    
    @staticmethod
    def storage_exists() -> bool:
        return os.path.exists(VaultStorage.VAULT_FILE)
```

**Explication:**
- `VaultController`: Point d'entree pour toutes les operations sur le coffre
- Gere l'authentification, les operations CRUD et la persistence

---

### 4. app/views/gui.py - Interfaces Graphiques

Contient les vues pour l'authentification et le tableau de bord.

```python
# app/views/gui.py - Extrait des classes principales

class LoginView:
    """Vue de connexion"""
    
    def __init__(self, parent, on_login_callback, on_check_new_vault_callback):
        self.parent = parent
        self.on_login = on_login_callback
        self.on_check_new = on_check_new_vault_callback
    
    def show(self):
        """Affiche la vue de connexion"""
        # Cree le frame principal
        self.frame = ctk.CTkFrame(self.parent, fg_color="#D2C4B4")
        self.frame.pack(fill="both", expand=True)
        
        # Cree le frame de connexion
        login_frame = ctk.CTkFrame(self.frame, fg_color="#AACDDC", border_width=2, border_color="#81A6C6")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Titre
        ctk.CTkLabel(login_frame, text="ErgoSecure", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Champ mot de passe
        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Mot de passe", show="*", width=250)
        self.password_entry.pack(pady=10)
        
        # Bouton valider
        ctk.CTkButton(login_frame, text="Valider", command=self._handle_login, fg_color="#81A6C6").pack(pady=10)


class DashboardView:
    """Vue principale du coffre"""
    
    def __init__(self, parent: ctk.CTk, controller):
        self.parent = parent
        self.controller = controller
    
    def show(self):
        """Affiche le tableau de bord"""
        self._create_header()
        self._create_controls()
        self._create_entries_frame()
        self.load_entries()
    
    def load_entries(self, entries=None):
        """Affiche les entrees"""
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        
        if entries is None:
            entries = self.controller.get_all_entries()
        
        for entry in entries:
            self._create_entry_card(entry)
```

**Explication:**
- `LoginView`: Formulaire de connexion/creation de mot de passe principal
- `DashboardView`: Tableau de bord avec liste des mots de passe et actions

---

### 5. main.py - Point d'Entree

Lance l'application et initialise les composants.

```python
# main.py
import customtkinter as ctk
from app.controllers.vault import VaultController
from app.views.gui import LoginView, DashboardView


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ErgoSecure - Gestionnaire de Mots de Passe")
        self.geometry("900x600")
        
        self.controller = None
        self.login_view = None
        self.dashboard_view = None
        
        self.show_login()
    
    def show_login(self):
        self.login_view = LoginView(
            self,
            on_login_callback=self.handle_login,
            on_check_new_vault_callback=self.check_new_vault
        )
        self.login_view.show()
    
    def handle_login(self, password: str):
        controller = VaultController(password)
        
        if controller.is_authenticated:
            self.controller = controller
            self.show_dashboard()
        else:
            self.login_view.show_error("Mot de passe incorrect")
    
    def show_dashboard(self):
        self.dashboard_view = DashboardView(self, self.controller)
        self.dashboard_view.show()
    
    def logout(self):
        if self.controller:
            self.controller.logout()
        self.controller = None
        self.show_login()


if __name__ == "__main__":
    app = App()
    app.mainloop()
```

**Explication:**
- Initialise l'application CustomTkinter
- Gere la navigation entre les vues
- Transmet les donnees entre vues et controleur

---

## Flux de Donnees

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                                │
│                     (App - Root)                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────────┐
    │ LoginView │   │Dashboard │   │VaultController│
    └─────┬─────┘   └────┬─────┘   └──────┬───────┘
          │              │                │
          └──────────────┼────────────────┘
                         ▼
               ┌─────────────────┐
               │   Vault          │
               │ (PasswordEntry) │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ VaultStorage    │
               │ (crypto.py)     │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  vault.enc      │
               │  (fichier)     │
               └─────────────────┘
```

---

## Couleurs de l'Interface

| Role | Couleur |
|------|---------|
| Primary | #81A6C6 |
| Secondary | #AACDDC |
| Tertiary | #F3E3D0 |
| Background | #D2C4B4 |
| Dark | #1A3263 |

---

## Premiere Utilisation

1. **Lancer l'application**: `python main.py`
2. **Creer le mot de passe principal**: Entrez un mot de passe d'au moins 6 caracteres
3. **Ajouter des entrees**: Cliquez sur "+ Ajouter" pour inserer vos premiers mots de passe
4. **Gerer**: Vous pouvez editer, supprimer, rechercher et copier vos mots de passe

---

## Fichier Genere

- `vault.enc`: Contient toutes vos donnees chiffrees
- Ce fichier est cree dans le meme repertoire que l'application
