import streamlit as st
import auth  # assumes auth.py is in the same folder

def login_ui():
    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Please enter both username and password.")
        else:
            success, role = auth.login(username, password)
            if success:
                st.success(f"Welcome {username}! You are logged in as a {role}.")
                # You can now redirect or show additional options based on role
            else:
                st.error("Invalid username or password.")

if __name__ == "__main__":
    login_ui()
