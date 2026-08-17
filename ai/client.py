"""LLM Client Factory & Multi-provider Registry (OpenAI & Google GenAI)."""

from openai import AsyncOpenAI
from google import genai
from ai.config import get_ai_config


def get_openai_client() -> AsyncOpenAI:
    """Instantiate and return configured AsyncOpenAI client."""
    config = get_ai_config()
    return AsyncOpenAI(api_key=config.get_openai_key())


def get_gemini_client() -> genai.Client:
    """Instantiate and return configured Google GenAI client."""
    config = get_ai_config()
    return genai.Client(api_key=config.get_gemini_key())
