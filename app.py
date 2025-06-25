import streamlit as st, os, pandas as pd
from auth import *
from utils import generate_otp
from database import init_db

st.set_page_config(layout="wide")
conn = init_db()

# Sessions
if "step" not in st.session_state: st.session_state.step = "login"
if "user" not in st.session_state: st.session_state.user = None

def show_login():
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login") and login(u,p):
        st.session_state.user = u
    else: st.error("Login failed or not verified")

def show_signup():
    st.subheader("📝 Sign Up")
    u, p, e, cnum = st.text_input("Username"), st.text_input("Password", type="password"), st.text_input("Email"), st.text_input("Contact")
    if st.button("Create"):
        try:
            add_user(u,p,e,cnum, is_admin=(len(list_all_users())==0))
            st.success("OTP sent; please verify.")
            st.session_state.step="verify"; st.session_state.temp_user=u
        except Exception as ex:
            st.error(ex)

def show_verify():
    st.subheader("🔁 Enter OTP")
    otp = st.text_input("OTP")
    if st.button("Verify") and verify_otp(st.session_state.temp_user, otp):
        st.success("Verified. Please login.")
        st.session_state.step="login"
    else:
        st.error("Wrong OTP")

# Initial
if not st.session_state.user:
    st.title("Welcome to Retail Dashboard")
    if st.session_state.step=="login": show_login()
    elif st.session_state.step=="signup": show_signup()
    else: show_verify()
    if st.button("Go to Sign Up") and st.session_state.step!="signup": st.session_state.step="signup"
    st.stop()

# Authenticated Section
u = st.session_state.user
st.sidebar.write(f"Hello, {u}")
if st.sidebar.button("Logout"):
    st.session_state.user=None; st.session_state.step="login"; st.experimental_rerun()

role = get_role(u)
st.title(f"{role.title()} Dashboard")

# File Upload on main screen
uploaded = st.file_uploader("Upload CSV", type="csv")
if uploaded:
    os.makedirs("uploads", exist_ok=True)
    fname = os.path.join("uploads", u + "_" + uploaded.name)
    with open(fname, "wb") as f: f.write(uploaded.getbuffer())
    import datetime; from auth import save_file
    save_file(u, fname)
    st.success("Saved!")
    df = pd.read_csv(fname)
    st.dataframe(df)
    # simple charts:
    if "revenue" in df.columns and "date" in df.columns:
        df["date"]=pd.to_datetime(df["date"])
        st.line_chart(df.groupby("date")["revenue"].sum())

# Viewing history
st.subheader("My Uploads")
for f, ts in list_user_files(u):
    st.write(f"{f} @ {ts}")

# Admin panel
if role=="admin":
    st.subheader("All Users")
    for user in list_all_users(): st.write("-", user)
    st.subheader("All Uploads")
    from auth import conn
    for un, fname, ts in conn.execute("SELECT username,filename,uploaded_at FROM files"):
        st.write(un, fname, ts)
