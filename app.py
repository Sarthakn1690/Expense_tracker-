import streamlit as st
import time
import pandas as pd
from database.db import create_tables
from services.auth_service import register_user, login_user
from services.expense_service import add_expense, get_user_expenses, delete_expense
from services.analytics_service import get_user_dataframe

create_tables()

st.set_page_config(page_title="Expense Tracker", layout="wide")

# Session timeout (10 minutes)
SESSION_TIMEOUT = 600

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.last_activity = None

def check_timeout():
    if st.session_state.logged_in:
        if time.time() - st.session_state.last_activity > SESSION_TIMEOUT:
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.warning("Session expired. Please login again.")

if st.session_state.logged_in:
    check_timeout()
    st.session_state.last_activity = time.time()

# ---------------- LOGIN / REGISTER ----------------

if not st.session_state.logged_in:
    st.title("🔐 Expense Tracker Login")

    menu = st.radio("Select Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Register":
        if st.button("Register"):
            if register_user(username, password):
                st.success("Registered successfully! Please login.")
            else:
                st.error("Username already exists.")

    if menu == "Login":
        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.last_activity = time.time()
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

# ---------------- MAIN APP ----------------

else:
    st.sidebar.title("Navigation")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()

    page = st.sidebar.selectbox(
        "Go to",
        ["Add Expense", "View Expenses", "Dashboard"]
    )

    user_id = st.session_state.user_id

    if page == "Add Expense":
        st.subheader("Add Expense")
        category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Other"])
        amount = st.number_input("Amount", min_value=0.0)
        note = st.text_input("Note")

        if st.button("Add"):
            add_expense(user_id, category, amount, note)
            st.success("Expense added!")

    elif page == "View Expenses":
        st.subheader("Your Expenses")
        data = get_user_expenses(user_id)

        if data:
            df = pd.DataFrame(data, columns=["ID", "User", "Date", "Category", "Amount", "Note"])
            st.dataframe(df)

            expense_id = st.number_input("Expense ID to delete", min_value=1)
            if st.button("Delete"):
                delete_expense(user_id, expense_id)
                st.success("Deleted!")
        else:
            st.info("No expenses yet.")

    elif page == "Dashboard":
        st.subheader("Analytics Dashboard")

        df = get_user_dataframe(user_id)

        if df.empty:
            st.warning("No data to show.")
        else:
            total = df["amount"].sum()
            st.metric("Total Expenses", f"₹ {total}")

            st.bar_chart(df.groupby("category")["amount"].sum())

            df["date"] = pd.to_datetime(df["date"])
            st.line_chart(df.groupby("date")["amount"].sum())

            st.pyplot(df.groupby("category")["amount"].sum().plot(kind="pie", autopct='%1.1f%%').get_figure())
