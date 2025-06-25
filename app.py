import streamlit as st
import pandas as pd
from auth import create_users_table, add_user, login_user, reset_password, validate_recovery
from utils import insert_sales_data, fetch_sales_data, get_kpis
from database import init_db
import plotly.express as px

# Setup
st.set_page_config("Retail Dashboard", layout="wide")
create_users_table()
init_db()

# Session Init
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = False
    st.session_state["username"] = ""
    st.session_state["forgot_mode"] = False

def logout():
    st.session_state["auth_status"] = False
    st.session_state["username"] = ""
    st.session_state["forgot_mode"] = False
    st.rerun()

def login_ui():
    with st.form("login_form"):
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = login_user(username, password)
            if user:
                st.session_state["auth_status"] = True
                st.session_state["username"] = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    if st.button("Forgot Password?"):
        st.session_state["forgot_mode"] = True
        st.rerun()

def signup_ui():
    with st.form("signup_form"):
        st.subheader("📝 Sign Up")
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        email = st.text_input("Email")
        contact = st.text_input("Contact Number")
        if st.form_submit_button("Register"):
            try:
                add_user(username, password, email, contact)
                st.success("Account created. Please login.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

def forgot_password_ui():
    st.subheader("🔁 Recover Password")
    username = st.text_input("Username")
    email = st.text_input("Registered Email")
    contact = st.text_input("Contact Number")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        if validate_recovery(username, email, contact):
            reset_password(username, new_pass)
            st.success("Password reset. Please log in.")
            st.session_state["forgot_mode"] = False
            st.rerun()
        else:
            st.error("Details do not match.")

def creative_welcome():
    st.markdown("""
    <div style='text-align:center'>
        <h1>Welcome to the 🛒 Retail Sales Intelligence Dashboard</h1>
        <p>Analyze your sales data, explore trends, and make data-driven decisions.</p>
        <img src='https://cdn-icons-png.flaticon.com/512/1170/1170576.png' width='150'/>
    </div>
    """, unsafe_allow_html=True)

# Main App
if not st.session_state["auth_status"]:
    creative_welcome()
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state["forgot_mode"]:
            forgot_password_ui()
        else:
            login_ui()
    with col2:
        signup_ui()
    st.stop()

# Logged-in UI
st.sidebar.success(f"Welcome, {st.session_state['username']}")
if st.sidebar.button("Logout"):
    logout()

st.title("📊 Retail Sales Dashboard")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="latin1")
    st.write("Uploaded Preview:", df.head())
    try:
        insert_sales_data(df)
        st.success("Uploaded and saved to database!")
    except Exception as e:
        st.error(f"Upload error: {e}")

df = fetch_sales_data()
if df.empty:
    st.warning("No sales data available. Please upload.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
st.sidebar.subheader("Filters")
region = st.sidebar.selectbox("Region", ["All"] + sorted(df["region"].dropna().unique()))
start = st.sidebar.date_input("Start Date", df["date"].min().date())
end = st.sidebar.date_input("End Date", df["date"].max().date())

filtered = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)]
if region != "All":
    filtered = filtered[filtered["region"] == region]

revenue, units, avg_price = get_kpis(filtered)
col1, col2, col3 = st.columns(3)
col1.metric("Revenue", f"${revenue:,.2f}")
col2.metric("Units Sold", units)
col3.metric("Avg Price", f"${avg_price:.2f}")

st.subheader("📈 Revenue Trend")
fig = px.line(filtered.groupby("date")["revenue"].sum().reset_index(), x="date", y="revenue")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🔥 Top Products")
top = filtered.groupby("product_id")["revenue"].sum().reset_index().nlargest(5, "revenue")
fig2 = px.bar(top, x="product_id", y="revenue", title="Top Products by Revenue")
st.plotly_chart(fig2, use_container_width=True)
