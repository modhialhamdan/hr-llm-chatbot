import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "db" / "hr.sqlite"
TABLE_NAME = "employees"

def find_csv() -> Path:
    csv_files = list(DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")
    # Pick the first CSV file found
    return csv_files[0]

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "db").mkdir(exist_ok=True)

    csv_path = find_csv()
    print("Using CSV:", csv_path.name)

    df = pd.read_csv(csv_path)

    # Clean column names for SQL safety
    df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]

    engine = create_engine(f"sqlite:///{DB_PATH}")
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=False)

    print("SQLite DB:", DB_PATH)
    print("Table:", TABLE_NAME)
    print("Rows:", len(df), "Cols:", len(df.columns))
    print("Columns:", list(df.columns)[:10], "...")


if __name__ == "__main__":
    main()
