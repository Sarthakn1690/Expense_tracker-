from database.db import get_connection
from datetime import datetime

def add_expense(user_id, category, amount, note):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")

    cursor.execute(
        "INSERT INTO expenses (user_id, date, time, category, amount, note) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, date, time_now, category, amount, note)
    )

    conn.commit()
    conn.close()


def get_user_expenses(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()

    conn.close()
    return rows


def delete_expense(user_id, expense_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id=? AND user_id=?",
        (expense_id, user_id)
    )

    conn.commit()
    conn.close()
