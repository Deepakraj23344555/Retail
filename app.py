import streamlit as st
import pandas as pd
from auth import *

st.set_page_config("Retail Sales Dashboard", layout="wide")

# Ensure user DB table exists
create_users_table()

# Initialize session state
if "auth_status" not in st.session_state:
    st.session_state.auth_status = False
    st.session_state.username = ""
    st.session_state.forgot_mode = False
    st.session_state.show_login = True

def logout():
    st.session_state.auth_status = False
    st.session_state.username = ""
    st.session_state.show_login = True
    st.rerun()

def login_ui():
    st.subheader("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        submit = st.form_submit_button("Login")
        if submit:
            if login_user(username, password):
                st.session_state.auth_status = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    if st.button("Forgot Password?"):
        st.session_state.forgot_mode = True
        st.session_state.show_login = False
        st.rerun()

def signup_ui():
    st.subheader("📝 Create an Account")
    with st.form("signup_form"):
        username = st.text_input("Choose Username", key="signup_user")
        password = st.text_input("Choose Password", type="password", key="signup_pass")
        email = st.text_input("Email")
        contact = st.text_input("Contact Number")
        submit = st.form_submit_button("Sign Up")
        if submit:
            try:
                add_user(username, password, email, contact)
                st.success("Account created! Please log in.")
                st.session_state.show_login = True
                st.rerun()
            except ValueError as e:
                st.error(str(e))

def forgot_password_ui():
    st.subheader("🔁 Recover Password")
    with st.form("recover_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        contact = st.text_input("Contact Number")
        new_password = st.text_input("New Password", type="password")
        submit = st.form_submit_button("Reset Password")
        if submit:
            if validate_recovery(username, email, contact):
                reset_password(username, new_password)
                st.success("Password reset. Please log in.")
                st.session_state.forgot_mode = False
                st.session_state.show_login = True
                st.rerun()
            else:
                st.error("Details not matched. Try again.")

def welcome_screen():
    st.markdown("""
    <div style='text-align:center'>
        <h1>🛍️ Welcome to the Retail Sales Dashboard</h1>
        <p>Upload your sales data and uncover insights</p>
        <img src='https://cdn-icons-png.flaticon.com/512/1170/1170576.png' width='100'/>
    </div>
    """, unsafe_allow_html=True)

# ---------- APP LOGIC ----------

if not st.session_state.auth_status:
    welcome_screen()
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.forgot_mode:
            forgot_password_ui()
        elif st.session_state.show_login:
            login_ui()
    with col2:
        if not st.session_state.forgot_mode:
            signup_ui()
    st.stop()

# -------- MAIN DASHBOARD --------

st.sidebar.success(f"Welcome, {st.session_state.username} 👋")
if st.sidebar.button("Logout"):
    logout()

st.title("📊 Retail Sales Dashboard")
uploaded_file = st.sidebar.file_uploader("Upload Sales CSV", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except:
        df = pd.read_csv(uploaded_file, encoding="latin1")

    st.write("🔎 Preview of Uploaded Data:")
    st.dataframe(df.head())

    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"])
            st.subheader("📈 Sales Over Time")
            sales = df.groupby("date")["revenue"].sum().reset_index()
            st.line_chart(sales.set_index("date"))
        except:
            st.warning("Couldn't convert 'date' column.")

    if "region" in df.columns:
        st.subheader("🌍 Revenue by Region")
        region_data = df.groupby("region")["revenue"].sum()
        st.bar_chart(region_data)

else:
    st.info("Please upload a CSV file to view insights.")
