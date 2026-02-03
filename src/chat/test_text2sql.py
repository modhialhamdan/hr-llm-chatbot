from src.chat.sql_runner import run_sql
from src.chat.schema_reader import get_schema_text
from src.llm.falcon_sql import generate_sql

QUESTION = "How many employees are there in total?"

def main():
    schema = get_schema_text()
    print("[test] schema loaded.")

    print("[test] generating SQL...")
    sql = generate_sql(QUESTION, schema)
    print("[test] Generated SQL:\n", sql)

    print("[test] running SQL...")
    cols, rows = run_sql(sql)
    print("[test] Result columns:", cols)
    print("[test] Result:", rows[:5])

if __name__ == "__main__":
    main()
