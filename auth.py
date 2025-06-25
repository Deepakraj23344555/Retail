import sqlite3
def init_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT,
        email TEXT, contact TEXT, role TEXT, is_verified INTEGER
      )''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, filename TEXT, uploaded_at TEXT
      )''')
    conn.commit()
    return conn
