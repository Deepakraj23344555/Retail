# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db
from utils import insert_sales_data, fetch_sales_data, get_kpis
from auth import create_users_table, add_user, login_user, view_all_users

# -------------------- INIT --------------------
create_users_table()
init_db()

# Persistent session variables
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# -------------------- AUTH SYSTEM --------------------
menu = (
    st.sidebar.selectbox("Menu", ["Login", "Sign Up"])
    if not st.session_state["auth_status"]
    else "Logout"
)

if menu == "Login":
    st.sidebar.header("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state["auth_status"] = True
            st.session_state["username"] = username
            st.sidebar.success(f"✅ Logged in as {username}")
            st.experimental_rerun()
        else:
            st.sidebar.error("❌ Incorrect username or password")

elif menu == "Sign Up":
    st.sidebar.header("📝 Create New Account")
    new_user = st.sidebar.text_input("New Username")
    new_pass = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Register"):
        try:
            add_user(new_user, new_pass)
            st.sidebar.success("🎉 Account created! Please login.")
            st.experimental_rerun()
        except ValueError as ve:
            st.sidebar.error(f"❌ {ve}")

elif menu == "Logout":
    st.session_state["auth_status"] = False
    st.session_state["username"] = ""
    st.success("You have been logged out.")
    st.experimental_rerun()

if not st.session_state["auth_status"]:
    st.warning("🔒 Please login to access the dashboard.")
    st.stop()

# -------------------- DASHBOARD --------------------
st.set_page_config(page_title="Retail Dashboard", layout="wide")
st.title(f"📊 Welcome {st.session_state['username']} to the Retail Sales Dashboard")

# Admin view of registered users
if st.session_state["username"] == "admin":
    st.subheader("👥 Registered Users")
    users = view_all_users()
    st.dataframe(pd.DataFrame(users, columns=["Username"]))

# File Upload
st.sidebar.header("📤 Upload Sales Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV File", type=["csv"])

if uploaded_file:
    try:
        try:
            df_upload = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            df_upload = pd.read_csv(uploaded_file, encoding='latin1')
        st.write("Preview of Uploaded Data:", df_upload.head())
        insert_sales_data(df_upload)
        st.sidebar.success("✅ Data uploaded successfully!")
    except ValueError as ve:
        st.sidebar.error(f"❌ Upload error: {ve}")
    except Exception as e:
        st.sidebar.error(f"❌ Error inserting data: {e}")

# Fetch data
df = fetch_sales_data()
if df.empty:
    st.warning("No data found. Please upload a CSV.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])

# Filters
st.sidebar.subheader("🔍 Filter Options")
region = st.sidebar.selectbox("Region", ["All"] + sorted(df['region'].dropna().unique()))
start_date = st.sidebar.date_input("Start Date", df["date"].min())
end_date = st.sidebar.date_input("End Date", df["date"].max())
filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
if region != "All":
    filtered_df = filtered_df[filtered_df["region"] == region]

# KPIs
st.subheader("📈 Key Performance Indicators")
total_rev, total_units, avg_price = get_kpis(filtered_df)
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"${total_rev:,.2f}")
col2.metric("📦 Units Sold", f"{total_units}")
col3.metric("🧮 Avg. Unit Price", f"${avg_price:,.2f}")

# Charts
st.subheader("📉 Revenue Over Time")
rev_trend = filtered_df.groupby("date")["revenue"].sum().reset_index()
fig1 = px.line(rev_trend, x="date", y="revenue", title="Daily Revenue")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("🏆 Top Products by Revenue")
top_products = (
    filtered_df.groupby("product_id")["revenue"]
    .sum().reset_index().sort_values(by="revenue", ascending=False).head(5)
)
fig2 = px.bar(top_products, x="product_id", y="revenue", title="Top 5 Products")
st.plotly_chart(fig2, use_container_width=True)

# Download
st.subheader("📥 Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "filtered_sales_data.csv", "text/csv")
