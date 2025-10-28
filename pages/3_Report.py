import streamlit as st
import pandas as pd
import plotly.express as px
from utils.expenseTracker import Account  
from utils.chatbot_ui import render_finbot_sidebar



if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in first.")
    st.stop()

user_email = st.session_state.user_email
db_name = f"{user_email}.db"
account = Account(db_name=db_name)

# Render FinBot in sidebar
render_finbot_sidebar(account, user_email)

st.title("Financial Reports")
st.write("A finance report of your cash.")
st.divider()
expenses_df = account.expenseList()
income_df = account.incomeList()


if not expenses_df.empty:
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
if not income_df.empty:
    income_df['date'] = pd.to_datetime(income_df['date'])

col1, col2 = st.columns(2)
with col1:
    if not expenses_df.empty:
      
        if not expenses_df.empty:
            category_data = expenses_df.groupby("category")["amount"].sum().reset_index()
            fig_expense_pie = px.pie(
                category_data,
                values="amount",
                names="category",
                title="Expenses by Category",
                hole=0.4
            )
            st.plotly_chart(fig_expense_pie)
        else:
            st.write("No expenses recorded yet.")

# Income Breakdown
with col2:
    if not income_df.empty:

      
        if not income_df.empty:
            income_data = income_df.groupby("source")["amount"].sum().reset_index()
            fig_income_pie = px.pie(
                income_data,
                values="amount",
                names="source",
                title="Income Breakdown by Category",
                hole=0.4
            )
            st.plotly_chart(fig_income_pie)



if not expenses_df.empty and not income_df.empty:
   

    expenses_df["month"] = expenses_df["date"].dt.strftime("%Y-%m")
    income_df["month"] = income_df["date"].dt.strftime("%Y-%m")

    monthly_expense = expenses_df.groupby("month")["amount"].sum().reset_index()
    monthly_income = income_df.groupby("month")["amount"].sum().reset_index()

    # Create an area chart (stacked)
    fig = px.area(
        pd.concat([monthly_expense.assign(Type="Expense"), monthly_income.assign(Type="Income")]),
        x="month",
        y="amount",
        color="Type",
        title="Monthly Expense vs Income Trend",
        line_group="Type", 
        markers=True
    )
    st.plotly_chart(fig)


# Bar Chart: Monthly Spending by Category

if not expenses_df.empty:
    
    category_monthly_data = expenses_df.groupby(["month", "category"])["amount"].sum().reset_index()
    fig_category_bar = px.bar(category_monthly_data, x="month", y="amount", color="category", barmode="group", title="Monthly Spending by Category")
    st.plotly_chart(fig_category_bar)



# Stacked Bar Chart: Income vs Expenses

if not expenses_df.empty and not income_df.empty:
  
    stacked_data = pd.concat([
        monthly_expense.assign(Type="Expense"),
        monthly_income.assign(Type="Income")
    ])
    fig_stacked_bar = px.bar(stacked_data, x="month", y="amount", color="Type", barmode="stack", title="Stacked Income vs Expenses")
    st.plotly_chart(fig_stacked_bar)
