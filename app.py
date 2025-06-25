import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db
from utils import insert_sales_data, fetch_sales_data, get_kpis
from auth import create_users_table, add_user, login_user, view_all_users

# Init
init_db()
create_users_table()

# Session Setup
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# Auth Section
if not st.session_state["auth_status"]:
    menu = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])
    if menu == "Login":
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["auth_status"] = True
                st.session_state["username"] = username
                st.sidebar.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials.")
    elif menu == "Sign Up":
        st.sidebar.subheader("Create Account")
        new_user = st.sidebar.text_input("New Username")
        new_pass = st.sidebar.text_input("New Password", type="password")
        if st.sidebar.button("Register"):
            try:
                add_user(new_user, new_pass)
                st.sidebar.success("Account created. Please login.")
                st.rerun()
            except ValueError as e:
                st.sidebar.error(str(e))
    st.stop()

# Logout
if st.sidebar.button("Logout"):
    st.session_state["auth_status"] = False
    st.session_state["username"] = ""
    st.rerun()

# Main App
st.set_page_config(page_title="Retail Dashboard", layout="wide")
st.title("📊 Retail Sales Dashboard")
st.write(f"Logged in as: **{st.session_state['username']}**")

# Admin Panel
if st.session_state["username"] == "admin":
    st.subheader("Registered Users")
    users = view_all_users()
    st.dataframe(pd.DataFrame(users, columns=["Username"]))

# Upload Section
st.sidebar.subheader("Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    try:
        df_upload = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        df_upload = pd.read_csv(uploaded_file, encoding="latin1")
    st.subheader("Uploaded Data Preview")
    st.write(df_upload.head())
    try:
        insert_sales_data(df_upload)
        st.success("✅ Data uploaded successfully.")
    except Exception as e:
        st.error(f"❌ Upload Error: {e}")

# Dashboard
df = fetch_sales_data()
if df.empty:
    st.warning("No data found. Please upload CSV.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])

# Filters
st.sidebar.subheader("Filters")
region = st.sidebar.selectbox("Region", ["All"] + sorted(df["region"].dropna().unique()))
start_date = st.sidebar.date_input("Start Date", df["date"].min().date())
end_date = st.sidebar.date_input("End Date", df["date"].max().date())
filtered = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
if region != "All":
    filtered = filtered[filtered["region"] == region]

# KPIs
st.subheader("Key Metrics")
rev, units, avg_price = get_kpis(filtered)
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${rev:,.2f}")
col2.metric("Units Sold", f"{units}")
col3.metric("Avg Unit Price", f"${avg_price:.2f}")

# Charts
st.subheader("Revenue Over Time")
trend = filtered.groupby("date")["revenue"].sum().reset_index()
fig1 = px.line(trend, x="date", y="revenue", title="Daily Revenue Trend")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Top Products by Revenue")
top_products = filtered.groupby("product_id")["revenue"].sum().reset_index().nlargest(5, "revenue")
fig2 = px.bar(top_products, x="product_id", y="revenue", title="Top 5 Products")
st.plotly_chart(fig2, use_container_width=True)

# Download
st.subheader("Download Filtered Data")
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_sales.csv", "text/csv")
