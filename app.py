# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db
from utils import insert_sales_data, fetch_sales_data, get_kpis

# Initialize database
init_db()

st.set_page_config(page_title="Retail Dashboard", layout="wide")
st.title("📊 Retail Sales Dashboard")

# Sidebar: Upload CSV
st.sidebar.header("📤 Upload Sales Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV File", type=["csv"])

if uploaded_file:
    try:
        # Try UTF-8, fallback to latin1
        try:
            df_upload = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            df_upload = pd.read_csv(uploaded_file, encoding='latin1')

        st.write("Preview of Uploaded Data:", df_upload.head())
        insert_sales_data(df_upload)
        st.sidebar.success("✅ Data uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")

# Fetch all data from DB
df = fetch_sales_data()

# Stop if no data
if df.empty:
    st.warning("No data found. Please upload a CSV file.")
    st.stop()

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# Sidebar filters
st.sidebar.subheader("🔍 Filter Options")
region = st.sidebar.selectbox("Region", options=["All"] + sorted(df['region'].unique()))
start_date = st.sidebar.date_input("Start Date", df["date"].min())
end_date = st.sidebar.date_input("End Date", df["date"].max())

# Apply filters
filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
if region != "All":
    filtered_df = filtered_df[filtered_df["region"] == region]

# Show KPIs
st.subheader("📈 Key Performance Indicators")
total_rev, total_units, avg_price = get_kpis(filtered_df)

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"${total_rev:,.2f}")
col2.metric("📦 Units Sold", f"{total_units}")
col3.metric("🧮 Avg. Unit Price", f"${avg_price:,.2f}")

# Revenue over time
st.subheader("📉 Revenue Over Time")
rev_trend = filtered_df.groupby("date")["revenue"].sum().reset_index()
fig1 = px.line(rev_trend, x="date", y="revenue", title="Daily Revenue")
st.plotly_chart(fig1, use_container_width=True)

# Top products
st.subheader("🏆 Top Products by Revenue")
top_products = (
    filtered_df.groupby("product_id")["revenue"]
    .sum().reset_index().sort_values(by="revenue", ascending=False).head(5)
)
fig2 = px.bar(top_products, x="product_id", y="revenue", title="Top 5 Products")
st.plotly_chart(fig2, use_container_width=True)

# Download CSV
st.subheader("📥 Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "filtered_sales_data.csv", "text/csv")
