import streamlit as st
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def get_conn():
    return sqlite3.connect("users.db", check_same_thread=False)

def create_users_table():
    conn = get_conn()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        email TEXT,
        contact_number TEXT,
        is_verified INTEGER DEFAULT 1,
        role TEXT DEFAULT 'user'
    )''')
    conn.commit()

def create_uploads_table():
    conn = get_conn()
    conn.execute('''CREATE TABLE IF NOT EXISTS uploads (
        username TEXT,
        filename TEXT,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()

def add_user(username, password, email, contact):
    conn = get_conn()
    conn.execute("INSERT INTO users(username, password, email, contact_number) VALUES (?, ?, ?, ?)", 
                 (username, generate_password_hash(password), email, contact))
    conn.commit()

def login(username, password):
    conn = get_conn()
    cursor = conn.execute("SELECT password, is_verified, role FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result and check_password_hash(result[0], password):
        if result[1]:
            return True, result[2]  # role
    return False, None

def login_ui():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        success, role = login(username, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Login failed or not verified.")
    if st.button("Go to Sign Up"):
        st.session_state.logged_in = False
        st.rerun()

def signup_ui():
    st.subheader("📝 Sign Up")
    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")
    email = st.text_input("Email")
    contact = st.text_input("Contact Number")
    if st.button("Register"):
        try:
            add_user(username, password, email, contact)
            st.success("Signup successful. Please log in.")
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("Username already exists.")

def forgot_password_ui():
    st.subheader("🔁 Recover Password")
    email = st.text_input("Enter registered Email")
    contact = st.text_input("Enter Contact Number")
    new_password = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        conn = get_conn()
        cursor = conn.execute("SELECT * FROM users WHERE email=? AND contact_number=?", (email, contact))
        if cursor.fetchone():
            conn.execute("UPDATE users SET password=? WHERE email=? AND contact_number=?", 
                         (generate_password_hash(new_password), email, contact))
            conn.commit()
            st.success("Password reset successfully. Please login.")
            st.rerun()
        else:
            st.error("Email or contact number not found.")
