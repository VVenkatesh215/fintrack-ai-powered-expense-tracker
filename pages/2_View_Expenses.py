import streamlit as st
from utils.expenseTracker import Account  
import time
from utils.chatbot_ui import render_finbot_sidebar

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in see your expenses")
    st.stop()

user_email = st.session_state.user_email
db_name = f"{user_email}.db"  

account = Account(db_name=db_name)

# Render FinBot in sidebar
render_finbot_sidebar(account, user_email)

st.title("Your Transactions")
st.divider()

# Expenses Section
st.subheader("View Expenses")
expenses_df = account.expenseList()
if expenses_df.empty:
    st.caption("No expenses to show!")
else:
    st.dataframe(expenses_df)

if not expenses_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("Edit Expense"):
            with st.form("edit_expense_form"):
                edit_exp_id = st.number_input("Expense ID to Edit", min_value=1, step=1, key="edit_exp_id")
                
                # Try to load existing data
                if edit_exp_id > 0 and edit_exp_id in expenses_df["id"].values:
                    existing_exp = expenses_df[expenses_df["id"] == edit_exp_id].iloc[0]
                    
                    edit_exp_name = st.text_input("Expense Title", value=existing_exp["name"])
                    edit_exp_date = st.date_input("Date", value=existing_exp["date"])
                    edit_exp_amount = st.number_input("Amount", min_value=0.0, value=float(existing_exp["amount"]))
                    edit_exp_des = st.text_area("Description", value=existing_exp["description"])
                    
                    # Get category index
                    categories = ["-","Food", "Personal", "Transport", "Investment", "Medicine", "Miscellaneous"]
                    cat_index = categories.index(existing_exp["category"]) if existing_exp["category"] in categories else 0
                    edit_exp_category = st.selectbox("Category", categories, index=cat_index)
                else:
                    st.info("Enter a valid Expense ID to edit")
                    edit_exp_name = st.text_input("Expense Title")
                    edit_exp_date = st.date_input("Date")
                    edit_exp_amount = st.number_input("Amount", min_value=0.0)
                    edit_exp_des = st.text_area("Description")
                    edit_exp_category = st.selectbox("Category", ["-","Food", "Personal", "Transport", "Investment", "Medicine", "Miscellaneous"])
                
                if st.form_submit_button("Update Expense"):
                    if edit_exp_id > 0 and edit_exp_id in expenses_df["id"].values:
                        if edit_exp_amount <= 0:
                            st.error("Amount must be greater than 0!")
                        elif edit_exp_category == "-":
                            st.error("Please select a valid category!")
                        else:
                            account.updateExpense(edit_exp_id, edit_exp_date, edit_exp_name, edit_exp_amount, edit_exp_category, edit_exp_des)
                            st.toast("Expense Updated Successfully!")
                            time.sleep(1.5)
                            st.rerun()
                    else:
                        st.error("Please enter a valid Expense ID")
    
    with col2:
        with st.expander("Delete Expense"):
            with st.form("delete_expense_form"):
                expense_id = st.number_input("Expense ID to Delete", min_value=0, step=1)
                if st.form_submit_button("Delete"):
                    account.deleteExpense(expense_id)
                    st.toast("Expense Deleted Successfully!")
                    time.sleep(1.5)
                    st.rerun()

# Income Section
st.subheader("View Income")
income_df = account.incomeList()
if income_df.empty:
    st.caption("No incomes to show!")
else:
    st.dataframe(income_df)

# Delete Income
if not income_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("Edit Income"):
            with st.form("edit_income_form"):
                edit_inc_id = st.number_input("Income ID to Edit", min_value=1, step=1, key="edit_inc_id")
                
                # Try to load existing data
                if edit_inc_id > 0 and edit_inc_id in income_df["id"].values:
                    existing_inc = income_df[income_df["id"] == edit_inc_id].iloc[0]
                    
                    edit_inc_name = st.text_input("Income Title", value=existing_inc["name"])
                    edit_inc_date = st.date_input("Date", value=existing_inc["date"])
                    edit_inc_amount = st.number_input("Amount", min_value=0.0, value=float(existing_inc["amount"]))
                    edit_inc_des = st.text_area("Description", value=existing_inc["description"])
                    
                    # Get source index
                    sources = ["-","Salary", "Family", "Investment", "Other"]
                    src_index = sources.index(existing_inc["source"]) if existing_inc["source"] in sources else 0
                    edit_inc_source = st.selectbox("Source", sources, index=src_index)
                else:
                    st.info("Enter a valid Income ID to edit")
                    edit_inc_name = st.text_input("Income Title")
                    edit_inc_date = st.date_input("Date")
                    edit_inc_amount = st.number_input("Amount", min_value=0.0)
                    edit_inc_des = st.text_area("Description")
                    edit_inc_source = st.selectbox("Source", ["-","Salary", "Family", "Investment", "Other"])
                
                if st.form_submit_button("Update Income"):
                    if edit_inc_id > 0 and edit_inc_id in income_df["id"].values:
                        if edit_inc_amount <= 0:
                            st.error("Amount must be greater than 0!")
                        elif edit_inc_source == "-":
                            st.error("Please select a valid income source!")
                        else:
                            account.updateIncome(edit_inc_id, edit_inc_date, edit_inc_name, edit_inc_amount, edit_inc_source, edit_inc_des)
                            st.toast("Income Updated Successfully!")
                            time.sleep(1.5)
                            st.rerun()
                    else:
                        st.error("Please enter a valid Income ID")
    
    with col2:
        with st.expander("Delete Income"):
            with st.form("delete_income_form"):
                income_id = st.number_input("Income ID to Delete", min_value=0, step=1)
                if st.form_submit_button("Delete"):
                    account.deleteIncome(income_id)
                    st.toast("Income Deleted Successfully!")
                    time.sleep(1.5)
                    st.rerun()
