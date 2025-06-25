import streamlit as st
import sqlite3
import auth
import dashboard

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# Initialize DB tables
auth.create_users_table()
auth.create_uploads_table()

st.set_page_config(page_title="Retail Dashboard", layout="wide")
st.title("🏪 Welcome to Retail Dashboard")

# Navigation
menu = ["Home", "Login", "Sign Up", "Forgot Password"]
if st.session_state.logged_in:
    menu = ["Dashboard", "Logout"]
choice = st.sidebar.selectbox("Navigate", menu)

if choice == "Home":
    st.markdown("### 📊 Analyze Retail Sales Data in Real-Time")
    st.info("Please log in or sign up to get started.")

elif choice == "Login":
    auth.login_ui()

elif choice == "Sign Up":
    auth.signup_ui()

elif choice == "Forgot Password":
    auth.forgot_password_ui()

elif choice == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.success("Logged out successfully.")
    st.rerun()

elif choice == "Dashboard":
    if st.session_state.logged_in:
        dashboard.show_dashboard(st.session_state.username, st.session_state.role)
    else:
        st.error("You need to log in first.")
