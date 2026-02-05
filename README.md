# HR Analytics LLM Chatbot

A practical HR analytics chatbot built on the IBM HR Attrition dataset.  
It answers HR questions by running real SQL queries against a local SQLite database, then uses an LLM (either Local Falcon GGUF or Groq API) to provide HR-friendly insights.
 
> Numbers come from SQLite.
> The LLM is only used for interpretation + conversational recommendations, not for calculating results.

---

## Features

- **Text-to-SQL** for HR analytics questions 
- **SQLite** local database 
- **Streamlit UI** chat interface
- **Conversation memory** — follow-up questions like *"What about Sales?"* reuse previous context automatically
- **Export chat transcript** to **TXT** + **PDF**
- **Sentiment analysis script** (Groq-based)
-  **Dual LLM providers**
  - Local Falcon GGUF (offline)
  - Groq API (cloud)

---

## Project Structure

```txt
hr-llm-chatbot/
├── assets/                  # Screenshots + demo GIF 
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
│       └── sentiment.py     # Sentiment analysis using Groq
├── requirements.txt         # pip dependencies
├── environment.yml          # (optional) conda env spec
├── .env.example             # example env vars 
└── README.md
```
## Requirements
طط
- Windows

- Conda recommended

- Python 3.11 recommended (best compatibility)

- Optional (for Local GGUF): llama-cpp-python installed successfully

## Environment Setup

1) Create / Activate Conda Environment

Option A — create fresh env (recommended)
```bash
conda create -n hr-llm311 python=3.11 -y
conda activate hr-llm311
```

Option B — if you already have an env
```bash
conda activate hr-llm311
```
2) Install Dependencies
```bash
python -m pip install -U pip
pip install -r requirements.txt
```

If you use Groq (cloud LLM):
```bash
pip install groq python-dotenv httpx
```

If you use Local Falcon GGUF (offline):
```bash
pip install llama-cpp-python
```

If llama-cpp-python fails to build:

You likely need Visual Studio Build Tools (C++ build tools).

If storage is tight, prefer Groq provider and skip local GGUF.

### Configure Secrets (.env)

Create a file named .env in the project root:

GROQ_API_KEY=YOUR_KEY_HERE


### Data Ingestion (CSV → SQLite)

Place your dataset in:

data/HR-Employee-Attrition.csv


Then run:
```bash
python src/ingest/load_to_sqlite.py
```

Expected output:

Creates database: db/hr.sqlite

Creates table: employees

Confirms rows + columns

Check DB quickly:
```bash
python -m src.chat.db_inspect
```

Run the App (Streamlit Chatbot)

From the project root:
```bash
streamlit run src/app.py
```

Open in browser:

Local: http://localhost:8501


## Example Questions

Try:

  - How many employees are in the dataset?

  - What percentage of employees who work overtime left the company?

  - What is the attrition rate by department?

  - Average monthly income in Sales

  - Follow-up: What about Research & Development?



## Model Comparison

| Aspect              | Groq API (Cloud)                     | Local Falcon GGUF (CPU)           |
|---------------------|--------------------------------------|-----------------------------------|
| Execution            | Cloud-based                          | Fully local                       |
| Speed                | Very fast                            | Slower (CPU-bound)                |
| Cost                 | API usage                            | Free after setup                  |
| Internet Required    | Yes                                  | No                                |
| Offline Support      | No                                   | Yes                               |
| Privacy              | Data sent to API                     | Data stays on local machine       |
| Setup Complexity     | Easy                                 | Medium–Hard (C++ build tools)     |
| Hardware Dependency  | None (cloud handled)                 | CPU (RAM & disk intensive)        |
| Best Use Case        | Demos, fast iteration, presentations | Offline analysis, privacy-focused |

## Why This Project?

This project demonstrates a **real-world HR analytics pipeline** where:
- Business questions are translated into **validated SQL**
- Results come from an actual database (not hallucinated)
- LLMs are used only for **interpretation, insights, and follow-up reasoning**

It is designed to be:
- Safe (read-only SQL)
- Explainable
- Suitable for academic, demo, or internal analytics use

## Demo

![HR Analytics Chatbot Demo](assets/HRChatbotDemo.gif)

---

## Chatbot Interface

![Chatbot Interface](assets/ChatbotInterface.png)

---

## Follow-up Questions

![Follow-up Question](assets/Chatbotinterface-FollowUpQuestion.png)


