"""LLM Client Factory & Provider Wrapper."""

from google import genai
from ai.config import get_ai_config


def get_gemini_client() -> genai.Client:
    """Instantiate and return configured Google GenAI client."""
    config = get_ai_config()
    return genai.Client(api_key=config.get_api_key_value())
