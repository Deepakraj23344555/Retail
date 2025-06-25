import streamlit as st
import pandas as pd
import sqlite3

def show_dashboard(username, role):
    st.subheader(f"📈 Welcome, {username} ({role})")
    uploaded_file = st.file_uploader("Upload Retail Sales CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            st.dataframe(df.head())
            conn = sqlite3.connect("users.db", check_same_thread=False)
            conn.execute("INSERT INTO uploads(username, filename) VALUES (?, ?)", 
                         (username, uploaded_file.name))
            conn.commit()
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {e}")

    if role == 'admin':
        show_admin_dashboard()
    else:
        show_user_history(username)

def show_user_history(username):
    st.subheader("📂 Your Upload History")
    conn = sqlite3.connect("users.db", check_same_thread=False)
    rows = conn.execute("SELECT filename, upload_time FROM uploads WHERE username=?", (username,)).fetchall()
    for row in rows:
        st.write(f"{row[0]} — {row[1]}")

def show_admin_dashboard():
    st.subheader("🛠 Admin Dashboard")
    conn = sqlite3.connect("users.db", check_same_thread=False)
    users = conn.execute("SELECT username, email, contact_number, role FROM users").fetchall()
    st.write("### Registered Users")
    st.dataframe(users)
