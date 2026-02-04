"""
Groq SQL Generator
Uses Groq API to generate SQL (much faster and more accurate than local Falcon)
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def generate_sql_with_groq(question: str, schema: str) -> str:
    """
    Generate SQL query using Groq API
    
    Args:
        question: User's natural language question
        schema: Database schema
        
    Returns:
        Valid SQL query string
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "-- Error: GROQ_API_KEY not found in .env file"
    
    try:
        client = Groq(api_key=api_key)
        
        # Build the prompt
        prompt = f"""You are an expert SQL developer specializing in SQLite.

Your task: Generate ONE valid SQLite SELECT query to answer the user's question.

STRICT RULES:
- Return ONLY the SQL query (no explanations, no markdown, no extra text)
- Use SELECT only (no INSERT/UPDATE/DELETE/DROP)
- Query MUST include a FROM clause
- Use exact table and column names from the schema
- For rates/percentages, calculate as: (count_condition / count_total * 100.0)
- Query must be executable as-is

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

SQL QUERY (SQLite syntax):"""

        # Call Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a SQL expert. Generate ONLY valid SQLite queries. No explanations."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Deterministic for SQL
            max_tokens=300
        )
        
        # Extract SQL
        sql = response.choices[0].message.content.strip()
        
        # Clean the SQL
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        # Remove any "SQL:" prefix
        if sql.upper().startswith("SQL:"):
            sql = sql[4:].strip()
        
        # Ensure it ends with semicolon
        if not sql.endswith(";"):
            sql += ";"
        
        print(f"[Groq SQL] Generated: {sql}")
        
        return sql
        
    except Exception as e:
        error_msg = f"-- Error generating SQL with Groq: {str(e)}"
        print(f"[Groq SQL] {error_msg}")
        return error_msg