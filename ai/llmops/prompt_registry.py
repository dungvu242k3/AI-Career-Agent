import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

class PromptRegistry:
    """Dynamic Prompt Registry using Langfuse Prompts.
    Allows A/B testing and updating prompts without redeploying code.
    """
    
    def __init__(self):
        self.enabled = False
        try:
            import os
            from langfuse import Langfuse
            if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
                self.langfuse = Langfuse()
                self.enabled = True
        except ImportError:
            self.langfuse = None

    def get_prompt(self, prompt_name: str, fallback_text: str = "") -> str:
        """Fetch prompt from Langfuse, fallback to local text if unavailable."""
        if not self.enabled:
            return fallback_text
            
        try:
            prompt = self.langfuse.get_prompt(prompt_name)
            if prompt:
                # Assuming prompt template has a 'text' or 'compile' method
                return prompt.compile()
        except Exception as e:
            logger.warning(f"Failed to fetch prompt '{prompt_name}' from Langfuse: {e}")
            
        return fallback_text

@lru_cache()
def get_prompt_registry() -> PromptRegistry:
    return PromptRegistry()
