"""Privacy-safe optional response cache.

CV ingestion and CV generation are intentionally never cacheable. Cache keys
are owner-scoped HMACs, rather than raw prompts, and both requests and values
must pass the PII guard before they can be stored.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from typing import Any

import redis

from ai.guardrails.prompt_shield import PromptShieldEngine
from be.config import get_settings


logger = logging.getLogger(__name__)
_NON_CACHEABLE_OPERATIONS = {"cv-ingestion", "cv-generation"}


class ScopedResponseCache:
    """Short-lived, owner-scoped cache for already de-identified analysis only."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl = min(max(ttl_seconds, 1), 300)
        self._shield = PromptShieldEngine()
        secret = get_settings().ai_cache_hmac_secret.get_secret_value()
        self.enabled = bool(secret)
        self._secret = secret.encode("utf-8")
        self.redis_client: redis.Redis | None = None
        if not self.enabled:
            logger.info("AI response cache disabled: AI_CACHE_HMAC_SECRET is not configured")
            return
        try:
            self.redis_client = redis.Redis.from_url(
                # The asynchronous application does not use this cache in the
                # request path. This compatibility utility is intentionally
                # synchronous for batch/worker callers only.
                os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                decode_responses=True,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
            )
            self.redis_client.ping()
        except Exception:
            self.enabled = False
            self.redis_client = None
            logger.warning("AI response cache disabled: Redis is unavailable")

    def _safe_for_cache(self, value: str) -> bool:
        result = self._shield.scan_and_sanitize(value)
        return result.is_safe and result.redacted_pii_count == 0

    def _key(
        self,
        *,
        user_id: int,
        operation: str,
        prompt: str,
        model: str,
        prompt_version: str,
        schema_version: str,
    ) -> str:
        material = "|".join(
            (str(user_id), operation, model, prompt_version, schema_version, prompt)
        ).encode("utf-8")
        digest = hmac.new(self._secret, material, hashlib.sha256).hexdigest()
        return f"ai:response-cache:v1:{user_id}:{digest}"

    def get(
        self,
        *,
        user_id: int,
        operation: str,
        prompt: str,
        model: str,
        prompt_version: str,
        schema_version: str,
    ) -> dict[str, Any] | None:
        if (
            not self.enabled
            or self.redis_client is None
            or user_id <= 0
            or operation in _NON_CACHEABLE_OPERATIONS
            or not self._safe_for_cache(prompt)
        ):
            return None
        try:
            value = self.redis_client.get(
                self._key(
                    user_id=user_id, operation=operation, prompt=prompt,
                    model=model, prompt_version=prompt_version, schema_version=schema_version,
                )
            )
            return json.loads(value) if value else None
        except Exception:
            logger.warning("AI response-cache read failed")
            return None

    def set(
        self,
        *,
        user_id: int,
        operation: str,
        prompt: str,
        model: str,
        prompt_version: str,
        schema_version: str,
        response_data: dict[str, Any],
    ) -> None:
        serialized = json.dumps(response_data, ensure_ascii=False, separators=(",", ":"))
        if (
            not self.enabled
            or self.redis_client is None
            or user_id <= 0
            or operation in _NON_CACHEABLE_OPERATIONS
            or not self._safe_for_cache(prompt)
            or not self._safe_for_cache(serialized)
        ):
            return
        try:
            self.redis_client.setex(
                self._key(
                    user_id=user_id, operation=operation, prompt=prompt,
                    model=model, prompt_version=prompt_version, schema_version=schema_version,
                ),
                self.ttl,
                serialized,
            )
        except Exception:
            logger.warning("AI response-cache write failed")


class SemanticCache:
    """Deprecated unsafe API retained as an always-disabled compatibility shim."""

    def __init__(self, *_: Any, **__: Any):
        self.enabled = False
        logger.warning("SemanticCache is disabled; use ScopedResponseCache with de-identified data")

    def get_cached_response(self, *_: Any, **__: Any) -> None:
        return None

    def set_cached_response(self, *_: Any, **__: Any) -> None:
        return None
