import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB = "users.db"

def get_user(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, email, contact):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO users(username, password, email, contact_number) VALUES (?, ?, ?, ?)",
              (username, generate_password_hash(password), email, contact))
    conn.commit()
    conn.close()

def verify_user(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET is_verified=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def login(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT password, is_verified FROM users WHERE username=?", (username,))
    data = c.fetchone()
    conn.close()
    if data and check_password_hash(data[0], password) and data[1] == 1:
        return True
    return False

def is_admin(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE username=?", (username,))
    is_admin_flag = c.fetchone()
    conn.close()
    return is_admin_flag and is_admin_flag[0] == 1
