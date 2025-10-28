import streamlit as st
import sqlite3
import time
from utils.expenseTracker import ExpenseManager
from utils.expenseTracker import IncomeManager
from utils.expenseTracker import Account
from auth import AuthManager


st.title("FinTrack")
st.write("An AI powered finance tracker.")

auth = AuthManager()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    login_btn = st.button("Login", key="login_btn")

    if login_btn:
        if email.strip() and password.strip():
            if auth.login_user(email, password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("Login successful! Redirecting...")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Invalid email or password.")
        else:
            st.error("Please enter both email and password.")

with tab2:
    st.subheader("Register")
    new_email = st.text_input("Email", key="register_email")
    new_password = st.text_input("Password", type="password", key="register_password")
    register_btn = st.button("Register", key="register_btn")

    if register_btn:
        if new_email.strip() and new_password.strip():
            if auth.register_user(new_email, new_password):
                st.success("Registration successful! Please log in.")
            else:
                st.error("Email already exists.")
        else:
            st.error("Please enter both email and password.")


if st.session_state.logged_in:
    st.success("Welcome to FinTrack!")
    st.info("Head to sidebar to use features")
    
    # Add logout button
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.success("Logged out successfully!")
        time.sleep(1)
        st.rerun()


db_name = "expenses.db"

conn = sqlite3.connect(db_name)
c = conn.cursor()

if st.session_state.logged_in:
    ExManager = ExpenseManager(db_name=db_name)
    InManager = IncomeManager(db_name=db_name)
    account = Account(db_name=db_name)
    st.toast("Welcome to FinTrack!")

conn.close()
