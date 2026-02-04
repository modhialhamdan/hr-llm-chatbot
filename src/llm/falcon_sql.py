'''
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
    '''
from src.chat.sql_runner import run_sql
from src.chat.schema_reader import get_schema_text
from src.chat.hr_formatter import format_hr_insight
from src.llm.falcon_chat import falcon_chat
from src.llm.falcon_sql import generate_sql  # ← ADD THIS IMPORT
from src.llm.qroq_client import groq_chat

def fetch_one(sql: str) -> int:
    _, rows = run_sql(sql)
    return int(rows[0][0])

def answer_question(question: str, provider: str = "local") -> str:
    """
    Smart router that uses Text-to-SQL for any data question
    """
    q = question.lower()
    
    # Check if it's a data question (needs database)
    data_keywords = [
        "how many", "count", "total", "average", "show", "list",
        "employees", "attrition", "salary", "department", "overtime",
        "what is", "calculate", "find", "get", "display"
    ]
    
    is_data_question = any(keyword in q for keyword in data_keywords)
    
#Data question → Use Text-to-SQL

    if is_data_question:
        try:
            # Get database schema
            schema = get_schema_text()
            
            # Generate SQL using LLM
            print(f"[Router] Generating SQL for: {question}")
            sql = generate_sql(question, schema)
            print(f"[Router] Generated SQL: {sql}")
            
            # Check if SQL generation failed
            if sql.startswith("--") or "error" in sql.lower():
                return (
                    "I couldn't generate a valid SQL query for that question.\n\n"
                    "Try rephrasing, for example:\n"
                    "- How many employees are there?\n"
                    "- What's the average salary by department?"
                )
            
            # Execute SQL
            cols, rows = run_sql(sql)
            
            # Format results
            if not rows:
                return "No results found in the database for that query."
            
            # Build response
            response = "**Query Results:**\n\n"
            
            # Show SQL (for transparency)
            response += f"```sql\n{sql}\n```\n\n"
            
            # Show data
            if len(rows) == 1 and len(cols) == 1:
                # Single value (like COUNT, AVG)
                response += f"**Answer:** {rows[0][0]}"
            else:
                # Multiple rows/columns
                response += f"**Data ({len(rows)} rows):**\n\n"
                
                # Create markdown table
                response += "| " + " | ".join(cols) + " |\n"
                response += "|" + "|".join(["---"] * len(cols)) + "|\n"
                
                # Add rows (limit to 10)
                for row in rows[:10]:
                    response += "| " + " | ".join(str(v) for v in row) + " |\n"
                
                if len(rows) > 10:
                    response += f"\n*Showing first 10 of {len(rows)} rows*\n"
            
            return response
            
        except Exception as e:
            return f"Error executing query: {str(e)}\n\nPlease rephrase your question."
    
    #  General HR advice question → Use LLM chat
    else:
        system_prompt = (
            "You are a professional HR consultant. "
            "Provide clear, actionable advice based on HR best practices."
        )
        
        if provider == "groq":
            return groq_chat(question, system_prompt)
        else:
            return falcon_chat(question, system_prompt)
