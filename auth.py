import sqlite3

# Connect to SQLite database
def get_db_connection():
    return sqlite3.connect("users.db")  # Make sure this file exists

# Login function
def login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure the table exists
    try:
        cursor.execute(
            "SELECT password, is_verified, role FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            db_password, is_verified, role = row
            if password == db_password:  # You can hash and verify for more security
                return True, role
        return False, None
    except sqlite3.OperationalError as e:
        print("Database error:", e)
        return False, None
