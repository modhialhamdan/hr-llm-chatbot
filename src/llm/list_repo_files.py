from huggingface_hub import list_repo_files

REPO_ID = "tensorblock/falcon-7b-instruct-GGUF"

def main():
    files = list_repo_files(REPO_ID)
    ggufs = [f for f in files if f.lower().endswith(".gguf")]

    print("Total files:", len(files))
    print("GGUF files:", len(ggufs))
    for f in ggufs:
        print(f)

if __name__ == "__main__":
    main()
