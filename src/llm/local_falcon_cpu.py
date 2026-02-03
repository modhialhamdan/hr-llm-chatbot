from pathlib import Path
from llama_cpp import Llama

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "falcon-local.gguf"

def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    print("Model size (GB):", round(MODEL_PATH.stat().st_size / (1024**3), 2))

    llm = Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_threads=8,   # adjust to your CPU cores
        verbose=False
    )

    system_prompt = (
        "You are a professional HR consultant. "
        "Answer clearly, concisely, and based on workforce analytics."
    )

    user_question = (
        "List three common reasons why employees leave organizations."
    )

    prompt = f"{system_prompt}\nQuestion: {user_question}\nAnswer:"

    output = llm(
        prompt,
        max_tokens=150,
        temperature=0.6
    )

    print("\nFalcon Response:\n")
    print(output["choices"][0]["text"])

if __name__ == "__main__":
    main()
