import os
import json
import hashlib
import logging
from typing import Any
import redis

logger = logging.getLogger(__name__)

class SemanticCache:
    """Redis-based caching layer for LLM responses to reduce cost and latency.
    Currently implements Exact Match (hash). Can be extended to use Redis Stack for true Semantic Similarity.
    """

    def __init__(self, ttl_seconds: int = 86400 * 7): # Default cache 7 days
        self.ttl = ttl_seconds
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            # Ping to check connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("SemanticCache enabled and connected to Redis.")
        except Exception as e:
            self.enabled = False
            logger.warning(f"SemanticCache disabled (Redis connection failed): {e}")

    def _generate_key(self, prompt: str, model: str) -> str:
        """Generate a deterministic exact-match hash key."""
        content_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        return f"cache:llm:{model}:{content_hash}"

    def get_cached_response(self, prompt: str, model: str) -> dict[str, Any] | None:
        """Retrieve cached response if exact match exists."""
        if not self.enabled:
            return None
        
        key = self._generate_key(prompt, model)
        try:
            data = self.redis_client.get(key)
            if data:
                logger.info(f"Cache HIT for model {model}")
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            
        return None

    def set_cached_response(self, prompt: str, model: str, response_data: dict[str, Any]):
        """Store LLM response in cache."""
        if not self.enabled:
            return
            
        key = self._generate_key(prompt, model)
        try:
            self.redis_client.setex(
                name=key,
                time=self.ttl,
                value=json.dumps(response_data)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")
