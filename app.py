import streamlit as st
import pandas as pd
from auth import *
import os

st.set_page_config("Retail Dashboard", layout="wide")

# 1. Create user table
create_users_table()

# 2. Session state
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = False
    st.session_state["username"] = ""
    st.session_state["forgot_mode"] = False

def logout():
    st.session_state["auth_status"] = False
    st.session_state["username"] = ""
    st.rerun()

# 3. UI Functions
def login_ui():
    with st.form("login"):
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if login_user(username, password):
                st.session_state["auth_status"] = True
                st.session_state["username"] = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    if st.button("Forgot Password?"):
        st.session_state["forgot_mode"] = True
        st.rerun()

def signup_ui():
    with st.form("signup"):
        st.subheader("📝 Create New Account")
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        email = st.text_input("Email")
        contact = st.text_input("Contact Number")
        if st.form_submit_button("Register"):
            try:
                add_user(username, password, email, contact)
                st.success("Account created. Please log in.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

def forgot_password_ui():
    st.subheader("🔁 Forgot Password")
    username = st.text_input("Username")
    email = st.text_input("Registered Email")
    contact = st.text_input("Contact Number")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        if validate_recovery(username, email, contact):
            reset_password(username, new_pass)
            st.success("Password updated. Please log in.")
            st.session_state["forgot_mode"] = False
            st.rerun()
        else:
            st.error("Details incorrect!")

def welcome_screen():
    st.markdown("""
    <div style='text-align:center'>
        <h1>🛍️ Retail Sales Dashboard</h1>
        <p>Upload, analyze and visualize your sales performance.</p>
        <img src='https://cdn-icons-png.flaticon.com/512/1170/1170576.png' width='120'/>
        <p style="color:gray;">Start by signing in or creating an account.</p>
    </div>
    """, unsafe_allow_html=True)

# 4. App logic
if not st.session_state["auth_status"]:
    welcome_screen()
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state["forgot_mode"]:
            forgot_password_ui()
        else:
            login_ui()
    with col2:
        signup_ui()
    st.stop()

# 5. Main App After Login
st.sidebar.success(f"Welcome, {st.session_state['username']}")
if st.sidebar.button("Logout"):
    logout()

st.title("📊 Retail Sales Dashboard")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="latin1")
    st.write("📄 Data Preview:", df.head())
else:
    st.info("Please upload a CSV file to begin.")
    st.stop()

# Optional data logic
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
    st.subheader("📈 Sales Over Time")
    chart = df.groupby("date")["revenue"].sum().reset_index()
    st.line_chart(chart.rename(columns={"revenue": "Revenue"}).set_index("date"))
else:
    st.warning("No 'date' column found in uploaded data.")

if "region" in df.columns:
    st.subheader("🌍 Revenue by Region")
    reg = df.groupby("region")["revenue"].sum()
    st.bar_chart(reg)
