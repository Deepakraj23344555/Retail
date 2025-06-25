import sqlite3
import hashlib

def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_users_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        email TEXT,
        contact_number TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(username, password, email, contact):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        raise ValueError("Username already exists.")
    c.execute("INSERT INTO users (username, password, email, contact_number) VALUES (?, ?, ?, ?)",
              (username, make_hash(password), email, contact))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, make_hash(password)))
    result = c.fetchone()
    conn.close()
    return result is not None

def reset_password(username, new_password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE username=?", (make_hash(new_password), username))
    conn.commit()
    conn.close()

def validate_recovery(username, email, contact):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND email=? AND contact_number=?", (username, email, contact))
    result = c.fetchone()
    conn.close()
    return result is not None
