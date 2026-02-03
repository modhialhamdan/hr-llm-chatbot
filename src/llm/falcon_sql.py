from pathlib import Path
from llama_cpp import Llama
from src.llm.sql_prompt import build_sql_prompt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "falcon-local.gguf"

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        print("[falcon] loading model...")
        _llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=2048,
            n_threads=8,
            n_batch=128,
            verbose=False,
        )
        print("[falcon] model loaded.")
    return _llm

def _clean_sql(text: str) -> str:
    sql = text.strip()
    # Remove code fences if any
    sql = sql.replace("```sql", "").replace("```", "").strip()
    # Take only first statement before blank line
    sql = sql.split("\n\n")[0].strip()
    # Ensure it ends without trailing comma
    if sql.endswith(","):
        sql = sql[:-1]
    return sql

def _needs_from(sql: str) -> bool:
    s = sql.lower()
    return s.startswith("select") and (" from " not in s)

def generate_sql(question: str, schema: str) -> str:
    llm = get_llm()

    prompt = build_sql_prompt(schema, question)
    print("[falcon] generating SQL...")
    out = llm(prompt, max_tokens=120, temperature=0.0, stop=["```", "\n\n"])
    sql = _clean_sql(out["choices"][0]["text"])
    print("[falcon] raw SQL:", sql)

    # If it forgot FROM, ask for a fix once
    if _needs_from(sql):
        fix_prompt = f"""
The SQL you wrote is incomplete (missing FROM clause).
Rewrite a COMPLETE SQLite SELECT query with a FROM clause.

Schema:
{schema}

Question:
{question}

Return ONLY the SQL.
SQL:
""".strip()
        print("[falcon] fixing SQL...")
        out2 = llm(fix_prompt, max_tokens=160, temperature=0.0, stop=["```", "\n\n"])
        sql = _clean_sql(out2["choices"][0]["text"])
        print("[falcon] fixed SQL:", sql)

    return sql
