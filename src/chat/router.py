from src.chat.sql_runner import run_sql
from src.chat.hr_formatter import format_hr_insight

def fetch_one(sql: str) -> int:
    _, rows = run_sql(sql)
    return int(rows[0][0])

def answer_question(question: str) -> str:
    q = question.lower()

    # MVP intent: overtime attrition rate
    if ("overtime" in q) and ("attrition" in q or "left" in q or "leave" in q) and ("rate" in q or "percentage" in q or "%" in q):
        total_overtime = fetch_one("SELECT COUNT(*) FROM employees WHERE OverTime = 'Yes';")
        left_overtime = fetch_one("SELECT COUNT(*) FROM employees WHERE OverTime = 'Yes' AND Attrition = 'Yes';")
        pct = (left_overtime / total_overtime * 100) if total_overtime else 0.0
        return format_hr_insight(total_overtime, left_overtime, pct)

    # fallback: basic safe count
    if "how many employees" in q or "total employees" in q:
        total = fetch_one("SELECT COUNT(*) FROM employees;")
        return f"The dataset contains {total} employees."

    return (
        "I can answer questions about the HR dataset. Try questions like:\n"
        "- 'How many employees are in the dataset?'\n"
        "- 'What is the attrition rate among employees who work overtime?'"
    )
