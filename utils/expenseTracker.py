import sqlite3
import pandas as pd
import streamlit as st

class ExpenseManager:

    def __init__(self, db_name):

        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Create the table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                date DATE,
                                amount REAL,
                                category TEXT,
                                description TEXT)''')
        self.conn.commit()

    def addExpense(self, date, name, amount, category, description): #WHAT IS THIS? :(
        self.cursor.execute('''INSERT INTO expenses (name, date, amount, category, description)
                               VALUES (?, ?, ?, ?, ?)''', 
                               (name, date, amount, category, description))
        self.conn.commit()

    def viewExpenses(self):
        query = "SELECT * FROM expenses"
        return pd.read_sql(query, self.conn)

    def deleteExpense(self, expense_id):
        self.cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        self.conn.commit()
    
    def updateExpense(self, expense_id, date, name, amount, category, description):
        self.cursor.execute('''UPDATE expenses 
                               SET name=?, date=?, amount=?, category=?, description=?
                               WHERE id=?''',
                               (name, date, amount, category, description, expense_id))
        self.conn.commit()
    
    def getExpenseById(self, expense_id):
        query = f"SELECT * FROM expenses WHERE id={expense_id}"
        result = pd.read_sql(query, self.conn)
        return result.iloc[0] if not result.empty else None


class IncomeManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Create the table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS income (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                date DATE,
                                amount REAL,
                                source TEXT,
                                description TEXT)''')
        self.conn.commit()

    def addIncome(self, date, name, amount, source, description):
        self.cursor.execute('''INSERT INTO income (name, date, amount, source, description)
                               VALUES (?, ?, ?, ?, ?)''', 
                               (name, date, amount, source, description))
        self.conn.commit()

    def viewIncome(self):
        query = "SELECT * FROM income"
        return pd.read_sql(query, self.conn)

    def deleteIncome(self, income_id):
        self.cursor.execute("DELETE FROM income WHERE id=?", (income_id,))
        self.conn.commit()
    
    def updateIncome(self, income_id, date, name, amount, source, description):
        self.cursor.execute('''UPDATE income 
                               SET name=?, date=?, amount=?, source=?, description=?
                               WHERE id=?''',
                               (name, date, amount, source, description, income_id))
        self.conn.commit()
    
    def getIncomeById(self, income_id):
        query = f"SELECT * FROM income WHERE id={income_id}"
        result = pd.read_sql(query, self.conn)
        return result.iloc[0] if not result.empty else None


class Account:
    def __init__(self, db_name):
        self.IncomeManager = IncomeManager(db_name)
        self.ExpenseManager = ExpenseManager(db_name)
        self.Balance = 0.0  

    def getBalance(self):
        total_income = self.IncomeManager.viewIncome()["amount"].sum()
        total_expense = self.ExpenseManager.viewExpenses()["amount"].sum()
        self.Balance = total_income - total_expense
        return self.Balance

    def addExpense(self, date, name, amount, category, description):
        self.ExpenseManager.addExpense(date, name, amount, category, description)
        self.Balance -= amount
        st.success(f"Expense added successfully!")

    def addIncome(self, date, name, amount, source, description):
        self.IncomeManager.addIncome(date, name, amount, source, description)
        self.Balance += amount
        st.success(f"Income added successfully!")

    def expenseList(self):
        return self.ExpenseManager.viewExpenses()

    def incomeList(self):
        return self.IncomeManager.viewIncome()

    def deleteExpense(self, expense_id):
        expenses = self.ExpenseManager.viewExpenses()
        if expenses.empty:
            st.warning("No expenses to delete.")
            return

        if expense_id in expenses["id"].values:
            amount = expenses.loc[expenses["id"] == expense_id, "amount"].iloc[0]
            self.ExpenseManager.deleteExpense(expense_id)
            self.Balance += amount
            st.success(f"Expense {expense_id} deleted successfully!")
        else:
            st.warning(f"Invalid Expense ID: {expense_id}")

    def deleteIncome(self, income_id):
        incomes = self.IncomeManager.viewIncome()
        if incomes.empty:
            st.warning("No income records to delete.")
            return

        if income_id in incomes["id"].values:
            amount = incomes.loc[incomes["id"] == income_id, "amount"].iloc[0]
            self.IncomeManager.deleteIncome(income_id)
            self.Balance -= amount
            st.success(f"Income {income_id} deleted successfully!")
        else:
            st.warning(f"Invalid Income ID: {income_id}")
    
    def updateExpense(self, expense_id, date, name, amount, category, description):
        expenses = self.ExpenseManager.viewExpenses()
        if expense_id in expenses["id"].values:
            old_amount = expenses.loc[expenses["id"] == expense_id, "amount"].iloc[0]
            self.ExpenseManager.updateExpense(expense_id, date, name, amount, category, description)
            # Adjust balance: add back old amount, subtract new amount
            self.Balance = self.Balance + old_amount - amount
            st.success(f"Expense {expense_id} updated successfully!")
        else:
            st.warning(f"Invalid Expense ID: {expense_id}")
    
    def updateIncome(self, income_id, date, name, amount, source, description):
        incomes = self.IncomeManager.viewIncome()
        if income_id in incomes["id"].values:
            old_amount = incomes.loc[incomes["id"] == income_id, "amount"].iloc[0]
            self.IncomeManager.updateIncome(income_id, date, name, amount, source, description)
            # Adjust balance: subtract old amount, add new amount
            self.Balance = self.Balance - old_amount + amount
            st.success(f"Income {income_id} updated successfully!")
        else:
            st.warning(f"Invalid Income ID: {income_id}")
    
    def getExpenseById(self, expense_id):
        return self.ExpenseManager.getExpenseById(expense_id)
    
    def getIncomeById(self, income_id):
        return self.IncomeManager.getIncomeById(income_id)

# transactions list
    def format_transactions_for_ai(self):
        expenses = self.ExpenseManager.viewExpenses()
        income = self.IncomeManager.viewIncome()
        
       
        formatted_expenses = expenses[['name', 'date', 'amount', 'category', 'description']].to_dict(orient='records')
        formatted_income = income[['name', 'date', 'amount', 'source', 'description']].to_dict(orient='records')
        
        # final dictionary to be returned
        transactions = {
            'income': formatted_income,
            'expenses': formatted_expenses
        }
        
        return transactions