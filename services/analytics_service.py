import pandas as pd
from database.db import get_connection

def get_dataframe():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM expenses", conn)
    conn.close()
    return df

def category_summary(df):
    return df.groupby("category")["amount"].sum()

def daily_summary(df):
    df["date"] = pd.to_datetime(df["date"])
    return df.groupby("date")["amount"].sum()
