def build_sql_prompt(schema: str, question: str) -> str:
    return f"""
You are a senior data analyst.
Write ONE valid SQLite query that answers the user's question.

Hard requirements:
- Output MUST be a complete SQL query.
- Use SELECT only (no INSERT/UPDATE/DELETE/DROP).
- The query MUST include a FROM clause.
- Use table name exactly as in the schema.
- Return ONLY the SQL query, nothing else.

Schema:
{schema}

User question:
{question}

SQL (SQLite):
""".strip()
