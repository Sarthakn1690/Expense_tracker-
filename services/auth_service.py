import bcrypt
from database.db import get_connection

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, stored_hash = user
        if bcrypt.checkpw(password.encode(), stored_hash):
            return user_id

    return None
