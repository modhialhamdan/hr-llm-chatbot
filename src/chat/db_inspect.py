import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "hr.sqlite"

def main():
    if not DB_PATH.exists():
        print("DB not found at:", DB_PATH)
        return

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [r[0] for r in cur.fetchall()]

    print("DB:", DB_PATH)
    print("Tables:", tables)

if __name__ == "__main__":
    main()
