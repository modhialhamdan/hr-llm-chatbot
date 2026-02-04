'''
from pathlib import Path
from llama_cpp import Llama

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "falcon-local.gguf"

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=2048,
            n_threads=8,
            n_batch=128,
            verbose=False
        )
    return _llm

def falcon_chat(prompt: str) -> str:
    llm = get_llm()
    system = "You are a professional HR consultant. Answer clearly and briefly."
    full_prompt = f"{system}\n\n{prompt}\n\nAnswer:"
    out = llm(full_prompt, max_tokens=220, temperature=0.3)
    return out["choices"][0]["text"].strip()

def falcon_chat(prompt: str, system_prompt: str = None) -> str:
    llm = get_llm()
    
    # Default system prompt
    if system_prompt is None:
        system_prompt = "You are a professional HR consultant. Answer clearly and briefly."
    
    full_prompt = f"{system_prompt}\n\n{prompt}\n\nAnswer:"
    out = llm(full_prompt, max_tokens=220, temperature=0.3)
    return out["choices"][0]["text"].strip()
    '''
from pathlib import Path
from llama_cpp import Llama

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "falcon-local.gguf"

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=2048,
            n_threads=8,
            n_batch=128,
            verbose=False
        )
    return _llm

def falcon_chat(prompt: str, system_prompt: str = None) -> str:
    """
    Chat with local Falcon model
    
    Args:
        prompt: User's message
        system_prompt: Optional system instructions
    """
    llm = get_llm()
    
    # Default system prompt if not provided
    if system_prompt is None:
        system_prompt = "You are a professional HR consultant. Answer clearly and briefly."
    
    full_prompt = f"{system_prompt}\n\nQuestion: {prompt}\n\nAnswer:"
    out = llm(full_prompt, max_tokens=220, temperature=0.3)
    return out["choices"][0]["text"].strip()
