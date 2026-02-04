import os
import re
from dotenv import load_dotenv
from groq import Groq

from src.chat.sql_runner import run_sql
from src.chat.schema_reader import get_schema_text
from src.llm.falcon_chat import falcon_chat
from src.llm.groq_client import groq_chat

load_dotenv()

# =========================
# Follow-up / context logic
# =========================

FOLLOWUP_TRIGGERS = [
    "what about", "how about", "and in", "and for", "same for", "same in",
    "only", "just", "for sales", "in sales", "in hr", "in human resources",
    "in research", "in r&d", "in research & development", "compare", "vs", "versus",
    "them", "those", "that", "it"
]

DEPARTMENT_HINTS = [
    "sales", "human resources", "research & development", "research and development", "r&d"
]

DATA_WORDS = [
    "how many", "count", "total", "number",
    "average", "avg", "mean",
    "rate", "percentage", "percent", "ratio",
    "max", "min", "highest", "lowest",
    "attrition", "overtime", "salary", "income", "department", "employees"
]

# Used to detect if the previous assistant answer was a DATA response
DATA_MARKERS_IN_ASSISTANT = [
    "**result:**", "**results", "rows):", "average", "rate:", "%", "count"
]


def _safe_lower(s: str) -> str:
    return (s or "").strip().lower()


def build_context(conversation_history: list, max_msgs: int = 8) -> str:
    if not conversation_history:
        return ""
    recent = conversation_history[-max_msgs:]
    return "\n".join(
        f"{m.role.upper()}: {m.content[:180]}"
        for m in recent
        if getattr(m, "role", None) in ["user", "assistant"]
    )


def last_user_data_question(conversation_history: list) -> str:
    """Return the most recent 'data-like' user question."""
    if not conversation_history:
        return ""

    for msg in reversed(conversation_history):
        if msg.role == "user":
            q = _safe_lower(msg.content)
            if any(k in q for k in DATA_WORDS):
                return msg.content.strip()
    return ""


def last_assistant_looks_like_data(conversation_history: list) -> bool:
    if not conversation_history:
        return False
    for msg in reversed(conversation_history):
        if msg.role == "assistant":
            txt = _safe_lower(msg.content)
            return any(m in txt for m in DATA_MARKERS_IN_ASSISTANT)
    return False


def is_followup_question(question: str) -> bool:
    q = _safe_lower(question)
    if not q:
        return False

    # strong signals
    if q.startswith(("what about", "how about", "and", "only", "same")):
        return True

    if any(t in q for t in FOLLOWUP_TRIGGERS):
        return True

    # mentions department without data words -> often follow-up
    if any(d in q for d in DEPARTMENT_HINTS) and not any(k in q for k in DATA_WORDS):
        return True

    return False


def rewrite_followup_to_full_question(current_q: str, prev_q: str) -> str:
    """
    Turn:
      prev: "What's the average salary?"
      cur:  "What about in Sales?"
    Into:
      "What's the average salary in Sales?"
    """
    cur = (current_q or "").strip()
    prev = (prev_q or "").strip()
    if not prev:
        return cur

    # If current already includes data words, keep as-is
    cur_l = _safe_lower(cur)
    if any(k in cur_l for k in DATA_WORDS):
        return cur

    # Try simple merge
    # Extract "in X" / "for X" phrase
    m = re.search(r"(in|for)\s+(.+)$", cur, flags=re.IGNORECASE)
    if m:
        tail = m.group(0).strip()  # "in Sales"
        # avoid duplicate "in Sales" if prev already has it
        if tail.lower() in prev.lower():
            return prev
        # add tail to prev
        if prev.endswith("?"):
            prev = prev[:-1]
        return f"{prev} {tail}?"

    # If no explicit "in/for", just append the whole followup
    if prev.endswith("?"):
        prev = prev[:-1]
    return f"{prev} ({cur})?"


# =========================
# SQL helpers
# =========================

def get_sample_data(limit=3):
    """Get sample data to help LLM understand the dataset."""
    try:
        cols, rows = run_sql(f"SELECT * FROM employees LIMIT {int(limit)};")
        sample = "\n".join(
            f"Sample row {i+1}: " + ", ".join(f"{col}={val}" for col, val in zip(cols, row))
            for i, row in enumerate(rows)
        )
        return sample
    except Exception:
        return "No sample data available"


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate SQL before execution."""
    sql_lower = (sql or "").lower().strip()

    if not sql_lower.startswith("select"):
        return False, "Query must start with SELECT"

    if " from " not in sql_lower:
        return False, "Query must include FROM clause"

    dangerous = ["drop", "delete", "insert", "update", "alter", "create", "truncate"]
    for word in dangerous:
        if f" {word} " in sql_lower or sql_lower.startswith(f"{word} "):
            return False, f"Dangerous operation not allowed: {word.upper()}"

    if "employees" not in sql_lower:
        return False, "Query must reference 'employees' table"

    if sql.count("(") != sql.count(")"):
        return False, "Unmatched parentheses"

    if not sql_lower.rstrip().endswith(";"):
        return False, "Query should end with semicolon"

    return True, ""


def generate_sql_with_validation(question: str, schema: str, context: str = "", max_retries: int = 2) -> tuple[str, str]:
    """
    Generate SQL with automatic validation and retry.
    Returns: (sql_query, explanation)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "-- Error: GROQ_API_KEY not found", "API key missing"

    client = Groq(api_key=api_key)
    sample_data = get_sample_data()

    context_section = ""
    if context:
        context_section = f"""
PREVIOUS CONVERSATION (use to resolve follow-ups like "what about in Sales?"):
{context}
"""

    previous_sql = ""
    previous_error = ""

    for attempt in range(max_retries + 1):
        try:
            if attempt == 0:
                prompt = f"""You are an expert SQL analyst specializing in SQLite and HR analytics.

Generate ONE valid SQLite SELECT query to answer the question.

CRITICAL RULES:
1. Return ONLY the SQL query (no explanations, no markdown, no extra text)
2. Use SELECT only (no INSERT/UPDATE/DELETE/DROP/ALTER/CREATE)
3. Must include FROM employees clause
4. Use exact column names from schema
5. For percentages: (COUNT(condition) * 100.0 / COUNT(*))
6. For "above average": use subqueries like (SELECT AVG(col) FROM employees)
7. Always end with semicolon
8. Use GROUP BY for aggregations by category

DATABASE SCHEMA:
{schema}

SAMPLE DATA:
{sample_data}

{context_section}

QUESTION:
{question}

Return ONLY the SQL:"""
            else:
                prompt = f"""The previous SQL had an error: {previous_error}

Generate a CORRECTED SQLite SELECT query.

Schema:
{schema}

Question:
{question}

Previous failed SQL:
{previous_sql}

Return ONLY the corrected SQL:"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Return ONLY valid SQLite queries."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=500,
            )

            sql = response.choices[0].message.content.strip()
            sql = sql.replace("```sql", "").replace("```", "").strip()

            # If model wrapped it weirdly, try to recover a SELECT line
            if not sql.lower().startswith("select"):
                for line in sql.splitlines():
                    if line.strip().lower().startswith("select"):
                        sql = line.strip()
                        break

            if not sql.endswith(";"):
                sql += ";"

            is_valid, error = validate_sql(sql)
            if is_valid:
                explain_prompt = f"""Explain this SQL query in 1 simple sentence:

Query: {sql}
Question: {question}

Explanation:"""

                explain_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": explain_prompt}],
                    temperature=0.3,
                    max_tokens=80,
                )
                explanation = explain_response.choices[0].message.content.strip()
                return sql, explanation

            previous_sql = sql
            previous_error = error

            if attempt == max_retries:
                return f"-- Validation error: {error}", error

        except Exception as e:
            if attempt == max_retries:
                return f"-- Generation error: {str(e)}", str(e)

    return "-- Failed after retries", "Failed to generate valid SQL"


def execute_with_fallback(sql: str) -> tuple[list, list, str]:
    """Execute SQL with basic fallback messaging."""
    try:
        cols, rows = run_sql(sql)
        return cols, rows, ""
    except Exception as e:
        error_str = str(e).lower()

        if "no such column" in error_str:
            m = re.search(r"no such column: (\w+)", error_str)
            if m:
                return [], [], f"Column '{m.group(1)}' doesn't exist. Please use exact schema column names."
            return [], [], "Column name error. Please rephrase using exact column names."

        if "no such table" in error_str:
            return [], [], "Table not found. Make sure you ran load_to_sqlite.py and DB path is correct."

        if "syntax error" in error_str:
            return [], [], "SQL syntax error. Try rephrasing your question."

        return [], [], str(e)


# =========================
# Classification
# =========================

def _classify_by_keywords(question: str) -> str:
    q = _safe_lower(question)
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "howdy"]
    if any(q.startswith(g) for g in greetings):
        return "GREETING"
    if any(k in q for k in DATA_WORDS):
        return "DATA"
    return "ADVICE"


def classify_question_type(question: str, context: str = "", conversation_history: list = None) -> str:
    """
    Smarter classifier:
    - If follow-up and previous looks like DATA => DATA
    - Else use LLM classifier if possible, fallback keywords
    """
    # Hard override: follow-up after data
    if conversation_history and is_followup_question(question) and last_assistant_looks_like_data(conversation_history):
        return "DATA"

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _classify_by_keywords(question)

    try:
        client = Groq(api_key=api_key)

        context_info = ""
        if context:
            context_info = f"""
PREVIOUS CONVERSATION:
{context}

If current question is a follow-up like "what about in Sales?", it is DATA.
"""

        prompt = f"""Classify this question into ONE category:

Question: "{question}"

{context_info}

Categories:
- DATA: needs database query, stats, follow-ups about stats
- ADVICE: recommendations/strategies (not stats follow-ups)
- GREETING: hello/hi

Return ONLY ONE WORD: DATA, ADVICE, or GREETING"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=5,
        )

        classification = response.choices[0].message.content.strip().upper()
        if classification in ["DATA", "ADVICE", "GREETING"]:
            return classification
        return "DATA"
    except Exception:
        return _classify_by_keywords(question)


# =========================
# Formatting
# =========================

def format_results(cols, rows, question: str) -> str:
    if len(rows) == 1 and len(cols) == 1:
        value = rows[0][0]
        col_name = cols[0].lower()
        ql = _safe_lower(question)

        if isinstance(value, (int, float)):
            if "avg" in col_name or "average" in col_name:
                if any(w in ql for w in ["salary", "pay", "income", "monthlyincome"]):
                    return f"**Average Salary:** ${value:,.2f}"
                if "age" in ql:
                    return f"**Average Age:** {value:.1f} years"
                return f"**Average:** {value:.2f}"

            if "rate" in col_name or "percent" in col_name or (isinstance(value, float) and value <= 100):
                return f"**Rate:** {value:.2f}%"

            if any(w in col_name for w in ["salary", "income", "pay"]):
                return f"**Result:** ${value:,.2f}"

            if isinstance(value, int):
                return f"**Result:** {value:,}"
            return f"**Result:** {value:,.2f}"

        return f"**Result:** {value}"

    # Multi-row => markdown table
    response = f"**Results ({len(rows)} rows):**\n\n"
    response += "| " + " | ".join(cols) + " |\n"
    response += "|" + "|".join(["---"] * len(cols)) + "|\n"

    display_limit = 25
    for row in rows[:display_limit]:
        response += "| " + " | ".join(str(v) for v in row) + " |\n"

    if len(rows) > display_limit:
        response += f"\n*Showing first {display_limit} of {len(rows)} rows*"

    return response


# =========================
# Main Router
# =========================

def answer_question(question: str, provider: str = "local", conversation_history: list = None) -> str:
    print(f"\n{'='*70}")
    print(f"[Router] Question: {question}")
    print(f"[Router] Provider: {provider}")

    context = build_context(conversation_history)

    # If follow-up, rewrite question using previous DATA question
    if conversation_history and is_followup_question(question):
        prev_q = last_user_data_question(conversation_history)
        if prev_q:
            rewritten = rewrite_followup_to_full_question(question, prev_q)
            if rewritten != question:
                print(f"[Router] Follow-up detected. Rewritten question:\n  {rewritten}")
                question = rewritten

    q_type = classify_question_type(question, context, conversation_history)
    print(f"[Router] Type: {q_type}")

    # GREETING
    if q_type == "GREETING":
        return (
            "**Hello! I'm your HR Analytics AI Assistant.**\n\n"
            "Try asking:\n"
            "• What's the average salary?\n"
            "• What about in Sales?\n"
            "• Attrition rate among overtime employees?\n"
        )

    # DATA
    if q_type == "DATA":
        try:
            schema = get_schema_text()
            print("[Router] Generating validated SQL...")
            sql, explanation = generate_sql_with_validation(question, schema, context)

            print(f"[Router] SQL: {sql}")
            print(f"[Router] Explanation: {explanation}")

            if sql.startswith("--"):
                return (
                    f"**I couldn't generate a valid SQL query.**\n\n"
                    f"**Issue:** {explanation}\n\n"
                    "**Try:**\n"
                    "• Use simpler phrasing\n"
                    "• Mention the metric (average/count/rate)\n"
                    "• Ask about one thing at a time\n"
                )

            cols, rows, error = execute_with_fallback(sql)
            if error:
                return (
                    f"**Query execution failed:**\n\n{error}\n\n"
                    "**Suggestions:**\n"
                    "• Rephrase your question\n"
                    "• Use exact column names\n"
                    "• Try a simpler question first\n"
                )

            if not rows:
                return "**No results found.**\n\nThe query ran successfully but returned no data."

            result_text = format_results(cols, rows, question)

            # Insight (LLM) - interpretation only
            insight_prompt = f"""As an HR expert, provide a brief insight (2-3 sentences) about this data.

Question: {question}
Result (sample): {rows[:3]}

Professional insight:"""

            insight = groq_chat(insight_prompt) if provider == "groq" else falcon_chat(insight_prompt)
            return result_text + "\n\n**HR Insight:**\n\n" + insight

        except Exception as e:
            return (
                f"**Unexpected error:**\n\n{str(e)}\n\n"
                "**Please try:**\n"
                "• Rephrasing your question\n"
                "• Asking a simpler question\n"
            )

    # ADVICE
    system_prompt = (
        "You are a senior HR consultant with 20+ years of experience. "
        "Provide specific, actionable advice. Be concise and practical."
    )

    if provider == "groq":
        return groq_chat(question, system_prompt)
    return falcon_chat(question, system_prompt)
