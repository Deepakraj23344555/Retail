# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db
from utils import insert_sales_data, fetch_sales_data, get_kpis

# Initialize database
init_db()

st.set_page_config(page_title="Retail Dashboard", layout="wide")
st.title("📈 Retail Business Analysis Dashboard")

# Sidebar: Upload
st.sidebar.header("📤 Upload Sales Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df_upload = pd.read_csv(uploaded_file)
    insert_sales_data(df_upload)
    st.sidebar.success("✅ Data uploaded successfully!")

# Fetch and show data
df = fetch_sales_data()

if df.empty:
    st.warning("No data found. Please upload a sales CSV file.")
    st.stop()

# Sidebar Filters
st.sidebar.subheader("🔍 Filter Options")
region = st.sidebar.selectbox("Region", options=["All"] + sorted(df['region'].unique().tolist()))
start_date = st.sidebar.date_input("Start Date", pd.to_datetime(df['date']).min())
end_date = st.sidebar.date_input("End Date", pd.to_datetime(df['date']).max())

# Apply filters
df['date'] = pd.to_datetime(df['date'])
filtered_df = df[
    (df['date'] >= pd.to_datetime(start_date)) &
    (df['date'] <= pd.to_datetime(end_date))
]

if region != "All":
    filtered_df = filtered_df[filtered_df["region"] == region]

# KPIs
total_rev, total_units, avg_price = get_kpis(filtered_df)

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"${total_rev:,.2f}")
col2.metric("📦 Units Sold", f"{total_units}")
col3.metric("📊 Avg. Unit Price", f"${avg_price:,.2f}")

# Charts
st.subheader("📉 Sales Over Time")
sales_trend = filtered_df.groupby("date")["revenue"].sum().reset_index()
fig = px.line(sales_trend, x="date", y="revenue", title="Daily Revenue")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🏆 Top Products by Revenue")
top_products = filtered_df.groupby("product_id")["revenue"].sum().reset_index().sort_values(by="revenue", ascending=False).head(5)
fig2 = px.bar(top_products, x="product_id", y="revenue", title="Top 5 Products")
st.plotly_chart(fig2, use_container_width=True)

# Download Option
st.subheader("📥 Download Filtered Report")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "filtered_report.csv", "text/csv")
