import sqlite3
import pandas as pd

def insert_sales_data(df):
    required_cols = ['date', 'store_id', 'product_id', 'quantity_sold', 'unit_price', 'revenue', 'region']
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    df = df[required_cols]
    conn = sqlite3.connect("retail_data.db")
    df.to_sql("sales_data", conn, if_exists="append", index=False)
    conn.close()

def fetch_sales_data():
    conn = sqlite3.connect("retail_data.db")
    df = pd.read_sql("SELECT * FROM sales_data", conn)
    conn.close()
    return df

def get_kpis(df):
    return df["revenue"].sum(), df["quantity_sold"].sum(), df["unit_price"].mean()
