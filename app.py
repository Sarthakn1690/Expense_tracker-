import streamlit as st
import pandas as pd
from database.db import create_table
from services.expense_service import add_expense, get_all_expenses, delete_expense
from services.analytics_service import get_dataframe, category_summary, daily_summary

create_table()

st.set_page_config(page_title="Expense Tracker", layout="wide")

st.title("💰 Expense Tracker")

# Sidebar
menu = st.sidebar.selectbox(
    "Navigation",
    ["Add Expense", "View Expenses", "Dashboard"]
)

# ---------------- ADD EXPENSE ----------------
if menu == "Add Expense":
    st.subheader("Add New Expense")

    categories = ["Food", "Travel", "Shopping", "Bills", "Other"]
    category = st.selectbox("Category", categories)
    amount = st.number_input("Amount", min_value=0.0)
    note = st.text_input("Note")

    if st.button("Add Expense"):
        if amount > 0:
            add_expense(category, amount, note)
            st.success("Expense added successfully!")
        else:
            st.error("Amount must be greater than 0")

# ---------------- VIEW EXPENSES ----------------
elif menu == "View Expenses":
    st.subheader("All Expenses")

    data = get_all_expenses()

    if data:
        df = pd.DataFrame(data, columns=["ID", "Date", "Category", "Amount", "Note"])
        st.dataframe(df)

        expense_id = st.number_input("Enter ID to Delete", min_value=1)
        if st.button("Delete Expense"):
            delete_expense(expense_id)
            st.success("Expense deleted!")
    else:
        st.info("No expenses found.")

# ---------------- DASHBOARD ----------------
elif menu == "Dashboard":
    st.subheader("Analytics Dashboard")

    df = get_dataframe()

    if df.empty:
        st.warning("No expenses to display.")
    else:
        st.dataframe(df)

        total = df["amount"].sum()
        st.metric("Total Expenses", f"₹ {total}")

        # Budget Alert
        BUDGET_LIMIT = 5000
        if total > BUDGET_LIMIT:
            st.error("⚠ Budget Exceeded!")

        # Category-wise Bar Chart
        st.subheader("Expenses by Category")
        cat_sum = category_summary(df)
        st.bar_chart(cat_sum)

        # Daily Line Chart
        st.subheader("Expenses Over Time")
        daily_sum = daily_summary(df)
        st.line_chart(daily_sum)

        # Pie Chart
        st.subheader("Expense Distribution")
        st.pyplot(cat_sum.plot(kind="pie", autopct='%1.1f%%').get_figure())

