"""Shared LLM clients with connection pooling and canonical configuration."""

from functools import lru_cache
from openai import AsyncOpenAI
from google import genai
from ai.config import get_ai_config


@lru_cache(maxsize=1)
def get_openai_client() -> AsyncOpenAI:
    """Return the process-wide async OpenAI client."""
    config = get_ai_config()
    key = config.get_openai_key()
    if not key or not key.strip():
        raise ValueError("OPENAI_API_KEY chưa được cấu hình trong file .env")
    return AsyncOpenAI(api_key=key.strip())


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    """Return the process-wide Gemini client."""
    config = get_ai_config()
    key = config.get_gemini_key()
    if not key or not key.strip():
        raise ValueError("GEMINI_API_KEY chưa được cấu hình trong file .env")
    return genai.Client(api_key=key.strip())

