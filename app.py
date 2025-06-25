import streamlit as st
import pandas as pd
import auth
import random

st.set_page_config("Retail Dashboard", layout="wide")

if "page" not in st.session_state: st.session_state.page = "home"
if "username" not in st.session_state: st.session_state.username = None
if "otp" not in st.session_state: st.session_state.otp = None
if "reset_user" not in st.session_state: st.session_state.reset_user = None

def home_ui():
    st.title("🛍️ Welcome to Retail Dashboard")
    st.markdown("### Empowering businesses with real-time insights 🔍")
    st.image("https://source.unsplash.com/800x300/?retail,data,analytics", use_column_width=True)
    if st.button("Login"): st.session_state.page = "login"
    if st.button("Sign Up"): st.session_state.page = "signup"
    if st.button("Forgot Password"): st.session_state.page = "reset"

def login_ui():
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if auth.login(u, p):
            st.session_state.username = u
            st.success("Login successful")
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Login failed or not verified")
    st.button("Go to Sign Up", on_click=lambda: st.session_state.update(page="signup"))

def signup_ui():
    st.subheader("📝 Sign Up")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    e = st.text_input("Email")
    c = st.text_input("Contact Number")
    if st.button("Sign Up"):
        if auth.user_exists(u):
            st.error("Username already exists")
        else:
            auth.add_user(u, p, e, c)
            st.session_state.otp = str(random.randint(100000, 999999))
            st.session_state.username = u
            st.session_state.page = "verify"
            st.rerun()

def verify_ui():
    st.subheader("📧 Enter OTP to Verify")
    st.info(f"Your OTP is: **{st.session_state.otp}**")  # You should send via email/SMS in real app
    otp_input = st.text_input("Enter OTP")
    if st.button("Verify"):
        if otp_input == st.session_state.otp:
            auth.verify_user(st.session_state.username)
            st.success("Account verified! Please login.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Invalid OTP")

def reset_ui():
    st.subheader("🔑 Reset Password")
    info = st.text_input("Enter email or contact number")
    if st.button("Send OTP"):
        user = auth.get_user_by_contact_email(info)
        if user:
            st.session_state.otp = str(random.randint(100000, 999999))
            st.session_state.reset_user = user
            st.success(f"OTP sent: {st.session_state.otp}")
        else:
            st.error("User not found")
    otp = st.text_input("Enter OTP")
    new_p = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        if otp == st.session_state.otp:
            auth.update_password(st.session_state.reset_user, new_p)
            st.success("Password updated. Please login.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Wrong OTP")

def dashboard_ui():
    st.subheader(f"📊 Welcome, {st.session_state.username}")
    uploaded = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded, encoding="latin-1")
        st.write("Data Preview", df.head())
        auth.save_upload(st.session_state.username, uploaded.name)
    st.markdown("### 📁 Upload History")
    rows = auth.get_uploads(st.session_state.username)
    for r in rows:
        st.markdown(f"**{r[2]}** - *{r[3]}*")

    if auth.is_admin(st.session_state.username):
        st.success("🛠️ Admin Access Enabled")
    st.button("Logout", on_click=lambda: st.session_state.update(username=None, page="home"))

# App flow
page = st.session_state.page
if page == "home": home_ui()
elif page == "login": login_ui()
elif page == "signup": signup_ui()
elif page == "verify": verify_ui()
elif page == "reset": reset_ui()
elif page == "dashboard": dashboard_ui()
