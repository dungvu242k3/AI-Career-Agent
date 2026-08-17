"""Prompts registry and loader."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(prompt_name: str) -> str:
    """Load prompt template text by filename."""
    file_path = PROMPTS_DIR / prompt_name
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt template '{prompt_name}' not found at {file_path}")
    return file_path.read_text(encoding="utf-8")
