import sqlite3
import pandas as pd

def insert_sales_data(df):
    expected = ['date', 'store_id', 'product_id', 'quantity_sold', 'unit_price', 'revenue', 'region']
    df = df[[col for col in df.columns if col in expected]]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

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
