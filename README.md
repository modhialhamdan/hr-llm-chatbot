# HR Analytics LLM Chatbot

A practical HR analytics chatbot built on the IBM HR Attrition dataset.  
It answers HR questions by running **real SQL queries** against a local **SQLite** database, then uses an LLM (either Local Falcon GGUF or Groq API) to provide HR-friendly insights.

> **Design principle:**  
> **Numbers come from SQLite.**  
> The **LLM is only used for interpretation + conversational recommendations**, not for calculating results.

---

## Features

- **Text-to-SQL** for HR analytics questions (safe `SELECT` only)
- **SQLite** local database (fast & reproducible)
- **Streamlit UI** chat interface
- **Conversation memory** (follow-up questions work)
- **Export chat transcript** to **TXT** + **PDF**
- **Sentiment analysis script** (Groq-based, no heavy Torch required)
-  **Dual LLM providers**
  - Local Falcon GGUF (offline)
  - Groq API (cloud, faster)

---

## Project Structure

```txt
hr-llm-chatbot/
├── assets/                  # Screenshots + demo GIF for README
├── data/                    # Dataset CSV (ignored in git)
├── db/
│   └── hr.sqlite            # SQLite database generated from CSV
├── models/                  # GGUF model files (ignored in git)
│   └── falcon-local.gguf
├── src/
│   ├── app.py               # Streamlit chatbot UI (main entry)
│   ├── ingest/
│   │   └── load_to_sqlite.py # Load CSV -> SQLite (creates employees table)
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── memory.py        # Chat memory (stores last N turns)
│   │   ├── router.py        # Main routing: classify → SQL → insight
│   │   ├── schema_reader.py # Loads schema text for SQL generation
│   │   ├── sql_runner.py    # Executes SQL against SQLite db
│   │   ├── exporter.py      # Export transcript to TXT/PDF
│   │   ├── db_inspect.py    # Inspect DB and list tables
│   │   ├── test_text2sql.py # Quick test: SQL generation + run
│   │   └── test_overtime_attrition.py # Validated KPI test
│   ├── llm/
│   │   ├── groq_client.py   # Groq chat wrapper
│   │   ├── falcon_chat.py   # Local GGUF chat wrapper (llama.cpp)
│   │   ├── falcon_sql.py    # Local GGUF SQL generation helper
│   │   ├── list_repo_files.py
│   │   └── download_falcon_gguf.py
│   └── analysis/
│       └── sentiment.py     # Sentiment analysis using Groq (lightweight)
├── requirements.txt         # pip dependencies
├── environment.yml          # (optional) conda env spec
├── .env.example             # example env vars (no secrets)
└── README.md
```
## Requirements
طط
- Windows

- Conda recommended

- Python 3.11 recommended (best compatibility)

- Optional (for Local GGUF): llama-cpp-python installed successfully

### Environment Setup

1) Create / Activate Conda Environment

Option A — create fresh env (recommended)

conda create -n hr-llm311 python=3.11 -y
conda activate hr-llm311


Option B — if you already have an env

conda activate hr-llm311

2) Install Dependencies
python -m pip install -U pip
pip install -r requirements.txt


If you use Groq (cloud LLM):

pip install groq python-dotenv httpx


If you use Local Falcon GGUF (offline):

pip install llama-cpp-python


If llama-cpp-python fails to build:
You likely need Visual Studio Build Tools (C++ build tools).
If storage is tight, prefer Groq provider and skip local GGUF.

Configure Secrets (.env)

Create a file named .env in the project root:

GROQ_API_KEY=YOUR_KEY_HERE


Data Ingestion (CSV → SQLite)

Place your dataset in:

data/HR-Employee-Attrition.csv


Then run:

python src/ingest/load_to_sqlite.py


Expected output:

Creates database: db/hr.sqlite

Creates table: employees

Confirms rows + columns

Check DB quickly:

python -m src.chat.db_inspect

Run the App (Streamlit Chatbot)

From the project root:

streamlit run src/app.py


Open in browser:

Local: http://localhost:8501

How Follow-up Questions Work (Memory)

The chatbot supports follow-up context, e.g.:

Q1: “What’s the average salary?”

Q2: “What about in Sales?”

Ensure app.py calls router with history:

answer = answer_question(
    user_text,
    provider=provider,
    conversation_history=st.session_state.memory.messages
)

Example Questions

Try:

How many employees are in the dataset?

What percentage of employees who work overtime left the company?

What is the attrition rate by department?

Average monthly income in Sales

Follow-up: What about Research & Development?

Export Chat (TXT / PDF)

In the sidebar you can export:

chat_transcript.txt

chat_transcript.pdf

Implementation:

src/chat/exporter.py generates TXT + PDF (ReportLab)

Sidebar buttons are defined in src/app.py

Sentiment Analysis (No Torch Needed)

Runs sentiment classification on an engineered text field combining:

Department

JobRole

OverTime

Attrition

Run:

python -m src.analysis.sentiment


Outputs a small dataframe with:

text

sentiment (POSITIVE / NEUTRAL / NEGATIVE)

score

source (groq)

This avoids heavy Torch installs and keeps environment light.

LLM Providers: Groq vs Local Falcon
Provider Switch (UI)

Inside the Streamlit sidebar:

local → Falcon GGUF via llama.cpp (offline)

groq → Groq API (cloud, fast)

Model Comparison
Aspect	Groq API	Local Falcon GGUF
Execution	Cloud	Fully local
Speed	Very fast	Slower (CPU)
Cost	API usage	Free after setup
Offline: Yes
Setup complexity	Easy	Medium/Hard (build tools)
Best for	Production demos	Offline & privacy
