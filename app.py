import streamlit as st
import pandas as pd
from utils.db_utils import init_db, insert_data, get_data
from charts.plot_utils import revenue_trend, revenue_by_store, product_pie_chart

st.set_page_config(layout="wide", page_title="Retail Analytics Dashboard")
st.title("🛍️ Retail Sales Analytics Dashboard")

# Initialize DB
init_db()

# Upload CSV
uploaded_file = st.file_uploader("Upload your sales CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    insert_data(df)
    st.success("✅ Data uploaded successfully!")

# Load data
df = get_data()

# Filters
with st.sidebar:
    st.header("🔍 Filter")
    date_range = st.date_input("Date range", [])
    store = st.selectbox("Select Store (Optional)", options=["All"] + df['store_id'].astype(str).unique().tolist())

# Apply filters
if date_range:
    df = df[(df['date'] >= str(date_range[0])) & (df['date'] <= str(date_range[1]))]

if store != "All":
    df = df[df['store_id'].astype(str) == store]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("📈 Total Revenue", f"₹{df['revenue'].sum():,.2f}")
col2.metric("📦 Units Sold", int(df['quantity_sold'].sum()))
col3.metric("🏆 Top Product", df.groupby("product_id")["revenue"].sum().idxmax())

# Charts
st.plotly_chart(revenue_trend(df), use_container_width=True)
st.plotly_chart(revenue_by_store(df), use_container_width=True)
st.plotly_chart(product_pie_chart(df), use_container_width=True)

# Data Preview
with st.expander("🔍 View Raw Data"):
    st.dataframe(df)
