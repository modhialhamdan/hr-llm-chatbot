import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "hr.sqlite"

def run_sql(query: str):
    q = query.strip().lower()
    if not q.startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
    return cols, rows
