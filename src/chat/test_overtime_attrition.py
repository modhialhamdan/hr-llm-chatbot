from src.chat.sql_runner import run_sql

def fetch_one(sql: str) -> int:
    cols, rows = run_sql(sql)
    return int(rows[0][0])

def main():
    total_overtime = fetch_one("SELECT COUNT(*) FROM employees WHERE OverTime = 'Yes';")
    left_overtime = fetch_one("SELECT COUNT(*) FROM employees WHERE OverTime = 'Yes' AND Attrition = 'Yes';")

    pct = (left_overtime / total_overtime * 100) if total_overtime else 0.0

    print("Total overtime employees:", total_overtime)
    print("Overtime employees who left:", left_overtime)
    print("Attrition rate (overtime):", round(pct, 2), "%")

if __name__ == "__main__":
    main()
