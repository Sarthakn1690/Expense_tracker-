import pandas as pd
from database.db import get_connection

def get_user_dataframe(user_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM expenses WHERE user_id=?",
        conn,
        params=(user_id,)
    )
    conn.close()
    return df
