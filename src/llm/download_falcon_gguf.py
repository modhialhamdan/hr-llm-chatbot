from pathlib import Path
from huggingface_hub import hf_hub_download

REPO_ID = "tensorblock/falcon-7b-instruct-GGUF"
FILENAME = "falcon-7b-instruct-Q3_K_M.gguf" 

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
OUT_PATH = MODELS_DIR / "falcon-local.gguf"

def main():
    MODELS_DIR.mkdir(exist_ok=True)

    print("Downloading GGUF from Hugging Face...")
    downloaded_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        local_dir=str(MODELS_DIR),
        resume_download=True,
    )

    src = Path(downloaded_path)
    if OUT_PATH.exists():
        OUT_PATH.unlink()
    src.rename(OUT_PATH)

    print("Downloaded to:", OUT_PATH)
    print("File size (bytes):", OUT_PATH.stat().st_size)

if __name__ == "__main__":
    main()
