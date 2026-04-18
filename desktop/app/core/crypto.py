import os
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoService:
    def __init__(self, password: str, salt: bytes = None):
        self.password = password
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key(password)

    def _derive_key(self, password: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt(self, data: dict) -> bytes:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        json_data = json.dumps(data).encode()
        padding = 16 - len(json_data) % 16
        json_data += bytes([padding] * padding)
        
        ciphertext = encryptor.update(json_data) + encryptor.finalize()
        return base64.b64encode(iv + self.salt + ciphertext)

    def decrypt(self, encrypted_data: bytes) -> dict:
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
    VAULT_FILE = "vault.enc"
    
    def __init__(self, crypto_service: CryptoService):
        self.crypto = crypto_service
    
    def save(self, data: dict):
        encrypted = self.crypto.encrypt(data)
        with open(self.VAULT_FILE, "wb") as f:
            f.write(encrypted)
    
    def load(self) -> dict:
        if not os.path.exists(self.VAULT_FILE):
            return {"entries": []}
        
        with open(self.VAULT_FILE, "rb") as f:
            encrypted = f.read()
        
        try:
            return self.crypto.decrypt(encrypted)
        except:
            return {"entries": []}
    
    def exists(self) -> bool:
        return os.path.exists(self.VAULT_FILE)
    
    def delete(self):
        if os.path.exists(self.VAULT_FILE):
            os.remove(self.VAULT_FILE)
