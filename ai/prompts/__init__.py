"""Prompts registry and loader."""

from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


@lru_cache(maxsize=32)
def load_prompt(prompt_name: str) -> str:
    """Load prompt template text by filename (supports .md and .txt)."""
    # 1. Direct match
    file_path = PROMPTS_DIR / prompt_name
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")

    # 2. Try with .md extension if omitted
    md_path = PROMPTS_DIR / f"{prompt_name}.md"
    if md_path.exists():
        return md_path.read_text(encoding="utf-8")

    # 3. Try with .txt extension as legacy fallback
    txt_path = PROMPTS_DIR / f"{prompt_name}.txt"
    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8")

    raise FileNotFoundError(f"Prompt template '{prompt_name}' not found in {PROMPTS_DIR}")


def load_composed_prompt(*prompt_names: str, separator: str = "\n\n---\n\n") -> str:
    """Load and compose multiple prompt files into a single instruction string.

    Args:
        *prompt_names: Variable number of prompt filenames to load and concatenate.
        separator: String used to join prompt sections (default: markdown horizontal rule).

    Returns:
        Single composed prompt string with all sections joined.
    """
    return separator.join(load_prompt(name) for name in prompt_names)
