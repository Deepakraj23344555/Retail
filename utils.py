# utils.py
import sqlite3
import pandas as pd

def insert_sales_data(df):
    conn = sqlite3.connect("retail_data.db")
    df.to_sql("sales_data", conn, if_exists="append", index=False)
    conn.close()

def fetch_sales_data():
    conn = sqlite3.connect("retail_data.db")
    df = pd.read_sql("SELECT * FROM sales_data", conn)
    conn.close()
    return df

def get_kpis(df):
    total_revenue = df["revenue"].sum()
    total_units = df["quantity_sold"].sum()
    avg_unit_price = df["unit_price"].mean()
    return total_revenue, total_units, avg_unit_price
