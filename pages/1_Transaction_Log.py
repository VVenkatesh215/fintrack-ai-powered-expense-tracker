import streamlit as st
from utils.expenseTracker import Account  
import time  
import datetime
from utils.chatbot_ui import render_finbot_sidebar


if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to continue :)")
    st.stop()

user_email = st.session_state.user_email
db_name = f"{user_email}.db"  
account = Account(db_name=db_name)

# Render FinBot in sidebar
render_finbot_sidebar(account, user_email)



st.title("Transactions Log")
st.divider()

# Initialize UI session state for expanders and form fields
if "expense_expanded" not in st.session_state:
    # keep expense expander open by default so user can add easily
    st.session_state.expense_expanded = True
if "income_expanded" not in st.session_state:
    st.session_state.income_expanded = True

if "balance" not in st.session_state:
    st.session_state.balance = account.getBalance()  # Fetch from database

# If a submit handler requested a form reset on previous run, perform it before widgets are created
if st.session_state.get("reset_expense_form", False):
    st.session_state.exName = ""
    st.session_state.exDate = datetime.date.today()
    st.session_state.exAmount = 0.0
    st.session_state.exDes = ""
    st.session_state.exCategory = "-"
    st.session_state.reset_expense_form = False

if st.session_state.get("reset_income_form", False):
    st.session_state.InName = ""
    st.session_state.InDate = datetime.date.today()
    st.session_state.InAmount = 0.0
    st.session_state.InDes = ""
    st.session_state.InSource = "-"
    st.session_state.reset_income_form = False


formatted_balance = f"₹{st.session_state.balance:.2f}"
st.write(f"Current Balance: {formatted_balance}")

# Add Expense
with st.expander("Add New Expense", expanded=st.session_state.expense_expanded):
    with st.form("expense_form"):
        # use explicit keys so we can clear fields after submit
        exName = st.text_input("Expense Title", key="exName")
        exDate = st.date_input("Date Of Expense", key="exDate")
        exAmount = st.number_input("Amount Spent", min_value=0.0, key="exAmount")
        exDes = st.text_area("Description", key="exDes")
        exCategory = st.selectbox("Category of expense", ("-","Food", "Personal", "Transport", "Investment", "Medicine", "Miscellaneous"), key="exCategory")
        submit_expense = st.form_submit_button("Add Expense")

        if submit_expense:
            # Validate inputs
            if exAmount <= 0:
                st.error("Amount must be greater than 0!")
            elif exCategory == "-":
                st.error("Please select a valid category!")
            elif not exName.strip():
                st.error("Please enter an expense title!")
            else:
                # Add expense to DB
                account.addExpense(exDate, exName, exAmount, exCategory, exDes)
                st.session_state.balance -= exAmount  # Deduct from balance
                st.toast("Expense Added Successfully!")
                # keep the expander open so user can add another expense
                st.session_state.expense_expanded = True
                # request a reset on the next run (do NOT set widget keys now)
                st.session_state.reset_expense_form = True
                time.sleep(1.0)
                st.rerun()


# Add Income
with st.expander("⬇ Add New Income", expanded=st.session_state.income_expanded):
    with st.form("income_form"):
        InName = st.text_input("Income Title", key="InName")
        InDate = st.date_input("Income Date", key="InDate")
        InAmount = st.number_input("Amount Received", min_value=0.0, key="InAmount")
        InDes = st.text_area("Description", key="InDes")
        InSource = st.selectbox("Source Of Income", ("-","Salary", "Family", "Investment", "Other"), key="InSource")
        submit_income = st.form_submit_button("Add Income")

        if submit_income:
            # Validate inputs
            if InAmount <= 0:
                st.error("Amount must be greater than 0!")
            elif InSource == "-":
                st.error("Please select a valid income source!")
            elif not InName.strip():
                st.error("Please enter an income title!")
            else:
                account.addIncome(InDate, InName, InAmount, InSource, InDes)
                st.session_state.balance += InAmount  # Add to balance
                st.toast("Income Added Successfully!")
                # keep income expander open for additional entries
                st.session_state.income_expanded = True
                # request a reset on the next run (do NOT set widget keys now)
                st.session_state.reset_income_form = True
                time.sleep(1.0)
                st.rerun()




























