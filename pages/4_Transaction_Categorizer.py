import streamlit as st
import pandas as pd
import datetime
import io
import time
from utils.expenseTracker import Account
from utils.chatbot_ui import render_finbot_sidebar


if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to use the Transaction Categorizer")
    st.stop()

user_email = st.session_state.user_email
db_name = f"{user_email}.db"
account = Account(db_name=db_name)

render_finbot_sidebar(account, user_email)

st.title("Transaction Categorizer")
st.write("Upload bank transactions (CSV / Excel). Select the relevant columns and preview how the rows will be classified before importing into your account.")
st.divider()


uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"], help="Columns should include at least amount and description; date column is optional.")

def _parse_amount(v):
    try:
        if pd.isna(v):
            return None
        s = str(v)
        # Remove common currency symbols and commas
        s = s.replace(',', '')
        s = s.replace('₹', '').replace('$', '').replace('€', '')
        # If value contains parentheses treat as negative (bank style)
        if '(' in s and ')' in s:
            s = s.replace('(', '-').replace(')', '')
        # Remove any non-numeric except minus and dot
        cleaned = ''.join(ch for ch in s if (ch.isdigit() or ch in '-.'))
        if cleaned in ['', '-', '.']:
            return None
        return float(cleaned)
    except Exception:
        return None


# Simple keyword-based category assignment
CATEGORY_KEYWORDS = {
    'Food': ['restaurant', 'cafe', 'dominos', 'pizza', 'burger', 'dine', 'canteen', 'kfc', 'canteen'],
    'Transport': ['uber', 'ola', 'taxi', 'metro', 'bus', 'fuel', 'petrol', 'petrolpump'],
    'Personal': ['shopping', 'flipkart', 'amazon', 'myntra', 'zomato', 'swiggy'],
    'Medicine': ['pharmacy', 'medic', 'pharmeasy', 'apollo'],
    'Investment': ['mutual', 'sip', 'investment', 'broker', 'demat'],
    'Salary': ['salary', 'payroll', 'paytm salary', 'salary credit'],
    'Miscellaneous': []
}

def guess_category(description):
    if not isinstance(description, str):
        return 'Miscellaneous'
    text = description.lower()
    for cat, keys in CATEGORY_KEYWORDS.items():
        for k in keys:
            if k in text:
                return cat
    return 'Miscellaneous'


if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    if df.empty:
        st.info("Uploaded file is empty.")
        st.stop()

    st.subheader("Preview of uploaded data")
    st.dataframe(df.head(50))

    cols = df.columns.tolist()
    amount_col = st.selectbox("Select Amount column", cols, help="Select the column that contains transaction amounts")
    cat_col = st.selectbox("Select Category column", cols, index=0 if len(cols)>0 else 0, help="Select column that contains transaction categories")
    date_col = st.selectbox("Select Date column (optional)", ["None"] + cols, index=0)
    type_col = st.selectbox("Select Type/Indicator column (optional)", ["None"] + cols, index=0)

    sign_handling = st.radio("How should debit/credit be detected?", options=[
        "Use sign of amount (negative = debit)",
        "Use Type/Indicator column (detect words like debit/dr/credit/cr)",
        "Try both (type column preferred)"
    ], index=2)

    use_preview_limit = st.number_input("Rows to preview", min_value=1, max_value=min(500, len(df)), value=min(50, len(df)))

    preview = df.copy()

    def detect_direction(row):
        a = _parse_amount(row.get(amount_col))
        t = None
        if type_col != "None":
            val = row.get(type_col)
            if isinstance(val, str):
                v = val.lower()
                if any(x in v for x in ['dr', 'debit', 'withdraw', 'payment']):
                    t = 'debit'
                elif any(x in v for x in ['cr', 'credit', 'deposit']):
                    t = 'credit'
        if sign_handling == "Use sign of amount (negative = debit)":
            if a is None:
                return 'unknown'
            return 'debit' if a < 0 else 'credit'
        elif sign_handling == "Use Type/Indicator column (detect words like debit/dr/credit/cr)":
            return t or 'unknown'
        else:
            if t is not None:
                return t
            if a is None:
                return 'unknown'
            return 'debit' if a < 0 else 'credit'

    preview['__parsed_amount__'] = preview[amount_col].apply(_parse_amount)
    preview['direction'] = preview.apply(detect_direction, axis=1)
    # single positive amount column
    preview['amount'] = preview['__parsed_amount__'].apply(lambda x: abs(x) if x is not None else None)
    # Use category from the selected file column
    preview['category'] = preview[cat_col].astype(str)

    st.subheader("Preview: detected direction and category")
    # Build a clean display DataFrame with unique column names to avoid duplicate-column errors
    display_df = pd.DataFrame({
        'date': preview[date_col] if date_col != "None" else 'N/A',
        'amount': preview['amount'],
        'category': preview['category'],
        'direction': preview['direction']
    }).head(int(use_preview_limit))
    st.dataframe(display_df)

    st.markdown("---")
    st.write("If the preview looks good you can import the rows. Rows with direction 'unknown' will be skipped unless you choose to import them as debit (expense) or credit (income) via the fallback option.")

    fallback_for_unknown = st.radio("Import unknown direction rows as:", options=["Skip", "Debit (Expense)", "Credit (Income)"], index=0)
    default_expense_category = st.selectbox("Default category for unmatched expenses", ["Miscellaneous", "Food", "Personal", "Transport", "Investment", "Medicine"], index=0)
    default_income_source = st.text_input("Default source label for imported incomes", value="Other")

    if st.button("Import Transactions"):
        added = 0
        skipped = 0
        errors = 0
        for idx, row in preview.iterrows():
            try:
                direction = row.get('direction')
                parsed = row.get('__parsed_amount__')
                if parsed is None:
                    skipped += 1
                    continue
                amt = abs(parsed)
                file_cat = str(row.get('category'))[:200]
                name = title_override.strip() if title_override.strip() else file_cat
                description = desc_override.strip() if desc_override.strip() else ""
                if date_col != "None":
                    raw_date = row.get(date_col)
                    try:
                        dt = pd.to_datetime(raw_date).date()
                    except Exception:
                        dt = datetime.date.today()
                else:
                    dt = datetime.date.today()

                if direction == 'debit':
                    cat = row.get('category') or default_expense_category
                    account.addExpense(dt, name, float(amt), cat, description)
                    added += 1
                elif direction == 'credit':
                    src = default_income_source
                    account.addIncome(dt, name, float(amt), src, description)
                    added += 1
                else:
                    # unknown
                    if fallback_for_unknown == 'Skip':
                        skipped += 1
                        continue
                    elif fallback_for_unknown == 'Debit (Expense)':
                        cat = row.get('category') or default_expense_category
                        account.addExpense(dt, name, float(amt), cat, description)
                        added += 1
                    else:
                        account.addIncome(dt, name, float(amt), default_income_source, description)
                        added += 1
                time.sleep(0.05)
            except Exception as e:
                errors += 1
                st.write(f"Row {idx} error: {e}")

        st.success(f"Import finished — added: {added}, skipped: {skipped}, errors: {errors}")
        st.rerun()

else:
    st.info("Upload a CSV or Excel file to start categorization.")
