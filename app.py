import streamlit as st
import time
import pandas as pd
from database.db import create_tables
from services.auth_service import register_user, login_user
from services.expense_service import add_expense, get_user_expenses, delete_expense
from services.analytics_service import get_user_dataframe

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Secure Expense Dashboard",
    page_icon="💰",
    layout="wide"
)

create_tables()

# ---------------- SESSION CONFIG ----------------
SESSION_TIMEOUT = 600  # 10 minutes

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
            st.rerun()

if st.session_state.logged_in:
    check_timeout()
    st.session_state.last_activity = time.time()

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:

    st.markdown("<h1 style='text-align:center;'>💰 Secure Expense Tracker</h1>", unsafe_allow_html=True)
    st.markdown("### Please Login or Register")

    menu = st.radio("", ["Login", "Register"], horizontal=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if menu == "Register":
            if st.button("Register", type="primary", use_container_width=True):
                if register_user(username, password):
                    st.success("Registered successfully! Please login.")
                else:
                    st.error("Username already exists.")

        if menu == "Login":
            if st.button("Login", type="primary", use_container_width=True):
                user_id = login_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.last_activity = time.time()
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

# ---------------- MAIN APPLICATION ----------------
else:

    st.sidebar.title("📊 Navigation")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()

    page = st.sidebar.selectbox(
        "Go to",
        ["Dashboard", "Add Expense", "View Expenses"]
    )

    user_id = st.session_state.user_id

    # ---------------- DASHBOARD ----------------
    if page == "Dashboard":

        st.title("📈 Expense Dashboard")

        df = get_user_dataframe(user_id)

        if df.empty:
            st.info("No expenses recorded yet.")
        else:
            total = df["amount"].sum()
            avg = df["amount"].mean()
            count = len(df)

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Expenses", f"₹ {total:.2f}")
            col2.metric("Average Expense", f"₹ {avg:.2f}")
            col3.metric("Total Transactions", count)

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Category Distribution")
                st.bar_chart(df.groupby("category")["amount"].sum())

            with col2:
                st.subheader("Daily Expense Trend")
                df["date"] = pd.to_datetime(df["date"])
                st.line_chart(df.groupby("date")["amount"].sum())

            st.subheader("Expense Breakdown")
            st.pyplot(
                df.groupby("category")["amount"]
                .sum()
                .plot(kind="pie", autopct="%1.1f%%")
                .get_figure()
            )

    # ---------------- ADD EXPENSE ----------------
    elif page == "Add Expense":

        st.title("➕ Add New Expense")

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "Category",
                ["Food", "Travel", "Bills", "Shopping", "Other"]
            )

        with col2:
            amount = st.number_input("Amount", min_value=0.0)

        note = st.text_input("Note")

        if st.button("Add Expense", type="primary"):
            add_expense(user_id, category, amount, note)
            st.success("Expense added successfully!")

    # ---------------- VIEW EXPENSES ----------------
    elif page == "View Expenses":

        st.title("📂 Your Expenses")

        data = get_user_expenses(user_id)

        if data:
            df = pd.DataFrame(
                data,
                columns=["ID", "User", "Date", "Category", "Amount", "Note"]
            )
            st.dataframe(df, use_container_width=True)

            st.divider()

            expense_id = st.number_input("Enter Expense ID to Delete", min_value=1)
            if st.button("Delete Expense"):
                delete_expense(user_id, expense_id)
                st.success("Expense deleted successfully!")
        else:
            st.info("No expenses available.")
