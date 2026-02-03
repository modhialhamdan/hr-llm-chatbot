import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "hr.sqlite"
TABLE_NAME = "employees"

def get_schema_text() -> str:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({TABLE_NAME});")
        cols = cur.fetchall()

    col_lines = []
    for _, name, col_type, *_ in cols:
        col_lines.append(f"- {name} ({col_type})")

    schema = f"Table: {TABLE_NAME}\nColumns:\n" + "\n".join(col_lines)
    return schema
