import streamlit as st
import pandas as pd
import os
import sqlite3
import auth

st.set_page_config(page_title="Retail Dashboard", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def show_welcome():
    st.markdown("## 👋 Welcome to **Retail Dashboard**")
    st.info("📊 Upload your sales data, view trends, and track KPIs — all in one place.")
    st.markdown("##### Please login or sign up to get started.")

def signup_ui():
    st.subheader("📝 Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    contact = st.text_input("Contact Number")
    if st.button("Sign Up"):
        if auth.get_user(username):
            st.error("Username already exists.")
        else:
            auth.add_user(username, password, email, contact)
            auth.verify_user(username)
            st.success("✅ Registered! Please login.")
            st.rerun()

def login_ui():
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if auth.login(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.success("✅ Logged in")
            st.rerun()
        else:
            st.error("Login failed or not verified")
    if st.button("Go to Sign Up"):
        signup_ui()

def forgot_password():
    st.subheader("🔒 Forgot Password")
    u = st.text_input("Enter your username")
    c = st.text_input("Enter registered contact/email")
    new_pass = st.text_input("Enter new password", type="password")
    if st.button("Reset Password"):
        user = auth.get_user(u)
        if user and (c == user[2] or c == user[3]):
            conn = sqlite3.connect("users.db")
            conn.execute("UPDATE users SET password=? WHERE username=?", 
                         (auth.generate_password_hash(new_pass), u))
            conn.commit()
            conn.close()
            st.success("Password updated! Please login.")
            st.rerun()
        else:
            st.error("Invalid username or contact.")

def upload_section():
    st.subheader("📤 Upload Sales Data")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
        df['username'] = st.session_state.username
        with sqlite3.connect("users.db") as conn:
            conn.execute("INSERT INTO uploads (username, filename) VALUES (?, ?)", 
                         (st.session_state.username, uploaded_file.name))
            conn.commit()
        st.dataframe(df)

def admin_dashboard():
    st.subheader("🛠️ Admin Dashboard")
    conn = sqlite3.connect("users.db")
    users_df = pd.read_sql("SELECT username, email, contact_number, is_verified, is_admin FROM users", conn)
    uploads_df = pd.read_sql("SELECT * FROM uploads", conn)
    conn.close()
    st.write("### Registered Users")
    st.dataframe(users_df)
    st.write("### File Upload History")
    st.dataframe(uploads_df)

def main_ui():
    st.title(f"Welcome, {st.session_state.username}")
    if auth.is_admin(st.session_state.username):
        admin_dashboard()
    upload_section()

# ---------- PAGE ROUTING ----------
st.title("Welcome to Retail Dashboard")
if not st.session_state.logged_in:
    col1, col2 = st.columns(2)
    with col1: login_ui()
    with col2: signup_ui()
    st.button("Forgot Password?", on_click=forgot_password)
else:
    main_ui()
