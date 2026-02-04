from src.chat.schema_reader import get_schema_text
from src.llm.falcon_sql import generate_sql

# Test question
question = "What's the turnover rate for people doing overtime?"

# Get schema
schema = get_schema_text()
print("=" * 60)
print("SCHEMA:")
print(schema)
print("=" * 60)

# Generate SQL
print("\nGenerating SQL for:", question)
sql = generate_sql(question, schema)

print("\n" + "=" * 60)
print("GENERATED SQL:")
print(sql)
print("=" * 60)

# Try to understand it
print("\nSQL Analysis:")
print("- Starts with SELECT?", sql.strip().lower().startswith("select"))
print("- Contains FROM?", " from " in sql.lower())
print("- Length:", len(sql))
print("- Has semicolon?", ";" in sql)