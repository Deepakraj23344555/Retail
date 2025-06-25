import sqlite3

def init_db():
    conn = sqlite3.connect('retail_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            store_id INTEGER,
            product_id INTEGER,
            quantity_sold INTEGER,
            unit_price REAL,
            revenue REAL,
            region TEXT
        )
    ''')
    conn.commit()
    conn.close()
