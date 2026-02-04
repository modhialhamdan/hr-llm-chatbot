import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def groq_chat(prompt: str, system_prompt: str = None) -> str:
    """
    Chat with Groq API
    
    Args:
        prompt: User's message
        system_prompt: Optional system instructions
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Groq API key not found. Please add GROQ_API_KEY to .env."

    # Default system prompt if not provided
    if system_prompt is None:
        system_prompt = "You are a professional HR consultant. Be concise and data-driven."

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[Groq error] {str(e)}"