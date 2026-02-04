import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

def find_csv() -> Path:
    files = list(DATA_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")
    return files[0]

def groq_sentiment(text: str) -> dict:
    """
    Returns:
      {"label": "POSITIVE"/"NEGATIVE"/"NEUTRAL", "score": float(0..1)}
    """
    from src.llm.groq_client import groq_chat

    prompt = (
        "You are a sentiment classifier.\n"
        "Classify the sentiment of the text as one of: POSITIVE, NEGATIVE, NEUTRAL.\n"
        "Return ONLY these two lines (no extra text):\n"
        "LABEL: <POSITIVE/NEGATIVE/NEUTRAL>\n"
        "CONFIDENCE: <0 to 1>\n\n"
        f"TEXT: {text}"
    )

    out = groq_chat(prompt)

    label = "NEUTRAL"
    conf = 0.5

    for line in out.splitlines():
        line = line.strip()
        if line.upper().startswith("LABEL:"):
            label = line.split(":", 1)[1].strip().upper()
        elif line.upper().startswith("CONFIDENCE:"):
            try:
                conf = float(line.split(":", 1)[1].strip())
            except ValueError:
                conf = 0.5

    if label not in {"POSITIVE", "NEGATIVE", "NEUTRAL"}:
        label = "NEUTRAL"

    conf = max(0.0, min(1.0, conf))
    return {"label": label, "score": conf}

def main():
    csv_path = find_csv()
    df = pd.read_csv(csv_path)

    # Feature Engineering: create a pseudo-text column from structured fields
    df["ProfileText"] = (
        "Department: " + df["Department"].astype(str)
        + " | JobRole: " + df["JobRole"].astype(str)
        + " | OverTime: " + df["OverTime"].astype(str)
        + " | Attrition: " + df["Attrition"].astype(str)
    )

    # Keep sample small (fast + cheap)
    sample = df["ProfileText"].sample(12, random_state=42).tolist()

    results = []
    for t in sample:
        pred = groq_sentiment(t)
        results.append({
            "text": t,
            "sentiment": pred["label"],
            "score": pred["score"],
            "source": "groq"
        })

    out = pd.DataFrame(results)
    print(out.to_string(index=False))

if __name__ == "__main__":
    main()
