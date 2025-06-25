# retail_dashboard/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")
st.title("🛒 Retail Sales Analytics Dashboard")

# Database setup
conn = sqlite3.connect("retail.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    store_id TEXT,
    product_id TEXT,
    category TEXT,
    quantity_sold INTEGER,
    revenue REAL
)
""")
conn.commit()

# File upload
st.sidebar.header("📂 Upload Sales Data")
file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if file:
    df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)
    st.subheader("Raw Uploaded Data")
    st.dataframe(df.head())

    # Save to DB
    df.to_sql("sales", conn, if_exists="append", index=False)
    st.success("Data uploaded and saved to database.")

# Filters
st.sidebar.header("📊 Filter Data")
start_date = st.sidebar.date_input("Start Date", datetime(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.today())

category_filter = st.sidebar.text_input("Product Category (leave blank for all)")
store_filter = st.sidebar.text_input("Store ID (leave blank for all)")

query = "SELECT * FROM sales WHERE date BETWEEN ? AND ?"
params = [start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")]

if category_filter:
    query += " AND category = ?"
    params.append(category_filter)
if store_filter:
    query += " AND store_id = ?"
    params.append(store_filter)

filtered_df = pd.read_sql_query(query, conn, params=params)

st.subheader("📈 Filtered Sales Data")
st.dataframe(filtered_df)

# KPIs
st.markdown("### 🧮 Key Performance Indicators")
col1, col2, col3 = st.columns(3)

with col1:
    total_revenue = filtered_df["revenue"].sum()
    st.metric("Total Revenue", f"₹ {total_revenue:,.2f}")

with col2:
    total_units = filtered_df["quantity_sold"].sum()
    st.metric("Total Units Sold", total_units)

with col3:
    top_product = (
        filtered_df.groupby("product_id")["quantity_sold"]
        .sum()
        .sort_values(ascending=False)
        .idxmax()
        if not filtered_df.empty else "N/A"
    )
    st.metric("Top-Selling Product", top_product)

# Charts
st.markdown("### 📊 Sales Visualizations")

if not filtered_df.empty:
    fig1 = px.line(
        filtered_df.groupby("date")["revenue"].sum().reset_index(),
        x="date", y="revenue", title="Revenue Over Time"
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        filtered_df.groupby("store_id")["revenue"].sum().reset_index(),
        x="store_id", y="revenue", title="Revenue by Store"
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.pie(
        filtered_df, names="category", values="revenue", title="Revenue by Category"
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No data available for selected filters.")
