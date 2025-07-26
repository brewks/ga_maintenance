# utils.py
import sqlite3
import pandas as pd
import json

DB_PATH = "C:/Users/workd/Desktop/ga_maintenance/PdM/ga_maintenance.db"

def load_df(query):
    """Run a SQL query and return a pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def validate_metrics(metrics_json):
    """Validate that a JSON string includes all required performance metric fields."""
    try:
        data = json.loads(metrics_json)
        required = ["precision", "recall", "accuracy", "f1_score"]
        return all(k in data for k in required)
    except (json.JSONDecodeError, TypeError):
        return False
