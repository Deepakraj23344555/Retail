import sqlite3
import hashlib
import random
import smtplib

DB = "users.db"

def make_hash(p): return hashlib.sha256(p.encode()).hexdigest()

def add_user(username, password, email, contact):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO users(username, password, email, contact_number) VALUES (?, ?, ?, ?)",
              (username, make_hash(password), email, contact))
    conn.commit()
    conn.close()

def login(u, p):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT password, is_verified FROM users WHERE username=?", (u,))
    res = c.fetchone()
    conn.close()
    return res and res[0] == make_hash(p) and res[1] == 1

def user_exists(u): return sqlite3.connect(DB).cursor().execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone()

def get_user_by_contact_email(email_or_phone):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE email=? OR contact_number=?", (email_or_phone, email_or_phone))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_password(username, new_password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE username=?", (make_hash(new_password), username))
    conn.commit()
    conn.close()

def verify_user(username):  # After OTP
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET is_verified=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def is_admin(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

def save_upload(username, filename):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO uploads(username, filename) VALUES (?, ?)", (username, filename))
    conn.commit()
    conn.close()

def get_uploads(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if username == "admin":
        c.execute("SELECT * FROM uploads ORDER BY uploaded_at DESC")
    else:
        c.execute("SELECT * FROM uploads WHERE username=? ORDER BY uploaded_at DESC", (username,))
    return c.fetchall()
