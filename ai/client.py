"""LLM Client Factory & Multi-provider Registry (OpenAI & Google GenAI)."""

from openai import AsyncOpenAI
from google import genai
from ai.config import get_ai_config


def get_openai_client() -> AsyncOpenAI:
    """Instantiate and return configured AsyncOpenAI client."""
    config = get_ai_config()
    key = config.get_openai_key()
    if not key or not key.strip():
        raise ValueError("OPENAI_API_KEY chưa được cấu hình trong file .env")
    return AsyncOpenAI(api_key=key.strip())


def get_gemini_client() -> genai.Client:
    """Instantiate and return configured Google GenAI client."""
    config = get_ai_config()
    key = config.get_gemini_key()
    if not key or not key.strip():
        raise ValueError("GEMINI_API_KEY chưa được cấu hình trong file .env")
    return genai.Client(api_key=key.strip())

