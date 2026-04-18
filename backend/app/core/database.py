import sqlite3
import hashlib
import os
from datetime import datetime

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(email: str, password: str):
    conn = get_db()
    c = conn.cursor()
    
    salt = os.urandom(32).hex()
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    created_at = datetime.utcnow().isoformat()
    
    try:
        c.execute("INSERT INTO users (email, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                  (email, password_hash, salt, created_at))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def verify_user(email: str, password: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT password_hash, salt FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    
    if row:
        password_hash = hashlib.sha256((password + row['salt']).encode()).hexdigest()
        return password_hash == row['password_hash']
    return False

def get_user(email: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, email FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "email": row[1]}
    return None

if __name__ == "__main__":
    init_db()
    print("Database initialized")
