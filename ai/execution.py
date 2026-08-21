"""Shared, privacy-safe execution boundary for LLM provider calls.

Provider adapters retain schema-specific request construction while this module
owns deadlines, retry classification, circuit breaking, and metadata-only
telemetry. It never logs prompts, responses, CVs, or job descriptions.
"""

from __future__ import annotations

import asyncio
from contextvars import ContextVar
import json
import logging
import random
import re
import time
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from typing import Awaitable, Callable, Generic, Literal, TypeVar

from ai.llmops.tracer import LLMOpsTracer


logger = logging.getLogger(__name__)
T = TypeVar("T")
Provider = Literal["openai", "gemini"]
_llmops_tracer: LLMOpsTracer | None = None


class AIStage(str, Enum):
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    INTERVIEW = "interview"


class AIErrorCode(str, Enum):
    INPUT_REJECTED = "AI_INPUT_REJECTED"
    TIMEOUT = "AI_TIMEOUT"
    PROVIDER_UNAVAILABLE = "AI_PROVIDER_UNAVAILABLE"
    BUDGET_EXCEEDED = "AI_BUDGET_EXCEEDED"
    INVALID_RESPONSE = "AI_INVALID_RESPONSE"


class AIExecutionError(ValueError):
    """Stable provider-neutral exception for API and worker boundaries."""

    def __init__(self, code: AIErrorCode, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


@dataclass(frozen=True)
class StagePolicy:
    timeout_seconds: float
    max_attempts: int
    max_input_chars: int


POLICIES: dict[AIStage, StagePolicy] = {
    AIStage.EXTRACTION: StagePolicy(20.0, 3, 30_000),
    AIStage.ANALYSIS: StagePolicy(18.0, 3, 24_000),
    AIStage.GENERATION: StagePolicy(25.0, 3, 28_000),
    AIStage.INTERVIEW: StagePolicy(8.0, 2, 8_000),
}


@dataclass(frozen=True)
class AIExecutionResult(Generic[T]):
    value: T
    trace_id: str
    provider: Provider
    attempts: int
    fallback_used: bool


class DistributedCircuitBreaker:
    """Shared Redis circuit breaker with an in-process development fallback."""

    def __init__(self, failure_threshold: int = 5, window_seconds: int = 60, recovery_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.window_seconds = window_seconds
        self.recovery_seconds = recovery_seconds
        self._local_failures: dict[str, tuple[int, float]] = {}
        self._local_open_until: dict[str, float] = {}

    @staticmethod
    def _key(stage: AIStage, provider: Provider, suffix: str) -> str:
        return f"ai:circuit:{stage.value}:{provider}:{suffix}"

    async def _redis(self):
        try:
            from be.core.redis_client import get_redis_client

            return await get_redis_client()
        except Exception:
            return None

    async def allow(self, stage: AIStage, provider: Provider) -> bool:
        redis_client = await self._redis()
        open_key = self._key(stage, provider, "open")
        if redis_client:
            try:
                return not bool(await redis_client.get(open_key))
            except Exception:
                pass
        return self._local_open_until.get(open_key, 0.0) <= time.monotonic()

    async def record_success(self, stage: AIStage, provider: Provider) -> None:
        redis_client = await self._redis()
        failures_key = self._key(stage, provider, "failures")
        if redis_client:
            try:
                await redis_client.delete(failures_key)
                return
            except Exception:
                pass
        self._local_failures.pop(failures_key, None)

    async def record_failure(self, stage: AIStage, provider: Provider) -> None:
        redis_client = await self._redis()
        failures_key = self._key(stage, provider, "failures")
        open_key = self._key(stage, provider, "open")
        if redis_client:
            try:
                failures = await redis_client.incr(failures_key)
                if failures == 1:
                    await redis_client.expire(failures_key, self.window_seconds)
                if failures >= self.failure_threshold:
                    await redis_client.set(open_key, "1", ex=self.recovery_seconds)
                return
            except Exception:
                pass

        now = time.monotonic()
        count, first_failure = self._local_failures.get(failures_key, (0, now))
        if now - first_failure > self.window_seconds:
            count, first_failure = 0, now
        count += 1
        self._local_failures[failures_key] = (count, first_failure)
        if count >= self.failure_threshold:
            self._local_open_until[open_key] = now + self.recovery_seconds


class PerUserUsageLedger:
    """Best-effort daily token/cost meter. It stores numeric counters only."""

    def __init__(self):
        self._local: dict[str, tuple[int, float]] = {}

    @staticmethod
    def _key(owner_user_id: int) -> str:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"ai:usage:{owner_user_id}:{day}"

    async def _redis(self):
        try:
            from be.core.redis_client import get_redis_client

            return await get_redis_client()
        except Exception:
            return None

    async def is_within_budget(self, owner_user_id: int | None) -> bool:
        if not owner_user_id:
            return True
        from be.config import get_settings

        key = self._key(owner_user_id)
        tokens, cost = self._local.get(key, (0, 0.0))
        redis_client = await self._redis()
        if redis_client:
            try:
                values = await redis_client.hmget(key, "tokens", "cost_usd")
                tokens = int(values[0] or 0)
                cost = float(values[1] or 0.0)
            except Exception:
                pass
        settings = get_settings()
        return tokens < settings.ai_daily_token_limit and cost < settings.ai_daily_cost_limit_usd

    async def record(self, owner_user_id: int | None, tokens: int, cost_usd: float) -> None:
        if not owner_user_id:
            return
        key = self._key(owner_user_id)
        current_tokens, current_cost = self._local.get(key, (0, 0.0))
        self._local[key] = (current_tokens + tokens, current_cost + cost_usd)
        redis_client = await self._redis()
        if redis_client:
            try:
                async with redis_client.pipeline(transaction=True) as pipe:
                    pipe.hincrby(key, "tokens", tokens)
                    pipe.hincrbyfloat(key, "cost_usd", cost_usd)
                    pipe.expire(key, 172_800)
                    await pipe.execute()
            except Exception:
                logger.warning("AI usage ledger update failed")


class AIExecutor:
    """Apply consistent execution semantics to every AI provider call."""

    def __init__(self, circuit_breaker: DistributedCircuitBreaker | None = None):
        self.circuit_breaker = circuit_breaker or DistributedCircuitBreaker()
        self.usage_ledger = PerUserUsageLedger()

    @staticmethod
    def _usage_from_response(value: object) -> tuple[int, int]:
        usage = getattr(value, "usage", None) or getattr(value, "usage_metadata", None)
        if usage is None:
            return 0, 0

        def get_int(*names: str) -> int:
            for name in names:
                raw = getattr(usage, name, None)
                if raw is None and isinstance(usage, dict):
                    raw = usage.get(name)
                if isinstance(raw, int):
                    return raw
            return 0

        return (
            get_int("prompt_tokens", "input_tokens", "prompt_token_count"),
            get_int("completion_tokens", "output_tokens", "candidates_token_count"),
        )

    @staticmethod
    def _estimated_cost_usd(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
        normalized = model_name.lower()
        if "gpt-4o-mini" in normalized:
            input_rate, output_rate = 0.15, 0.60
        elif "gpt-4o" in normalized:
            input_rate, output_rate = 2.50, 10.00
        elif "gemini" in normalized:
            # Conservative telemetry estimate; configure alerts on trends,
            # while provider billing remains the system of record.
            input_rate, output_rate = 0.30, 2.50
        else:
            return 0.0
        return round((prompt_tokens * input_rate + completion_tokens * output_rate) / 1_000_000, 6)

    @staticmethod
    def is_retryable(error: BaseException) -> bool:
        if isinstance(error, (asyncio.TimeoutError, TimeoutError, ConnectionError, OSError)):
            return True
        status_code = getattr(error, "status_code", None) or getattr(error, "status", None)
        if isinstance(status_code, int) and (status_code == 429 or status_code >= 500):
            return True
        # Some provider SDK wrappers expose only a message.  Keep this narrow:
        # validation and policy failures do not contain these transport terms.
        message = str(error).lower()
        return bool(
            re.search(r"\b(?:429|5\d\d)\b", message)
            or "timeout" in message
            or "connection reset" in message
        )

    @staticmethod
    def _error_code(error: BaseException) -> AIErrorCode:
        if isinstance(error, asyncio.TimeoutError):
            return AIErrorCode.TIMEOUT
        if isinstance(error, AIExecutionError):
            return error.code
        return AIErrorCode.PROVIDER_UNAVAILABLE if AIExecutor.is_retryable(error) else AIErrorCode.INVALID_RESPONSE

    async def _invoke(
        self,
        *,
        stage: AIStage,
        provider: Provider,
        operation: Callable[[], Awaitable[T]],
        trace_id: str,
        model_name: str,
        owner_user_id: int | None,
    ) -> tuple[T, int]:
        policy = POLICIES[stage]
        if not await self.circuit_breaker.allow(stage, provider):
            raise AIExecutionError(AIErrorCode.PROVIDER_UNAVAILABLE, "AI provider circuit is open", retryable=True)

        last_error: BaseException | None = None
        for attempt in range(1, policy.max_attempts + 1):
            started = time.perf_counter()
            try:
                value = await asyncio.wait_for(operation(), timeout=policy.timeout_seconds)
                await self.circuit_breaker.record_success(stage, provider)
                prompt_tokens, completion_tokens = self._usage_from_response(value)
                cost_usd = self._estimated_cost_usd(model_name, prompt_tokens, completion_tokens)
                await self.usage_ledger.record(owner_user_id, prompt_tokens + completion_tokens, cost_usd)
                self._record(
                    trace_id, stage, provider, attempt, "success", started,
                    model_name=model_name, prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens, cost_usd=cost_usd,
                )
                return value, attempt
            except BaseException as error:
                last_error = error
                retryable = self.is_retryable(error)
                self._record(trace_id, stage, provider, attempt, self._error_code(error).value, started, model_name=model_name)
                if retryable:
                    await self.circuit_breaker.record_failure(stage, provider)
                if not retryable or attempt == policy.max_attempts:
                    break
                await asyncio.sleep(min(2.0, 0.25 * (2 ** (attempt - 1))) + random.uniform(0, 0.15))

        assert last_error is not None
        if isinstance(last_error, asyncio.TimeoutError):
            raise AIExecutionError(AIErrorCode.TIMEOUT, "AI provider timed out", retryable=True) from last_error
        if self.is_retryable(last_error):
            raise AIExecutionError(AIErrorCode.PROVIDER_UNAVAILABLE, "AI provider is unavailable", retryable=True) from last_error
        if isinstance(last_error, AIExecutionError):
            raise last_error
        raise AIExecutionError(
            AIErrorCode.INVALID_RESPONSE,
            "AI provider returned an invalid response; xử lý thất bại trên cả 2 nhà cung cấp",
        ) from last_error

    async def run(
        self,
        *,
        stage: AIStage,
        primary_provider: Provider,
        primary: Callable[[], Awaitable[T]],
        fallback_provider: Provider | None = None,
        fallback: Callable[[], Awaitable[T]] | None = None,
        input_chars: int = 0,
        primary_model: str = "unknown",
        fallback_model: str = "unknown",
        owner_user_id: int | None = None,
    ) -> AIExecutionResult[T]:
        """Run a secondary provider only after retryable primary exhaustion."""
        effective_owner_user_id = owner_user_id if owner_user_id is not None else _current_owner_user_id.get()
        if input_chars > POLICIES[stage].max_input_chars:
            raise AIExecutionError(AIErrorCode.BUDGET_EXCEEDED, "AI input exceeds the stage budget")
        if not await self.usage_ledger.is_within_budget(effective_owner_user_id):
            logger.warning(
                "ai_budget_exhausted=%s",
                json.dumps({"owner_user_id": effective_owner_user_id, "stage": stage.value}),
            )
            raise AIExecutionError(AIErrorCode.BUDGET_EXCEEDED, "AI daily token or cost budget has been exhausted")

        trace_id = uuid.uuid4().hex
        _last_trace_id.set(trace_id)
        try:
            value, attempts = await self._invoke(
                stage=stage, provider=primary_provider, operation=primary, trace_id=trace_id,
                model_name=primary_model, owner_user_id=effective_owner_user_id,
            )
            return AIExecutionResult(value, trace_id, primary_provider, attempts, False)
        except AIExecutionError as error:
            if not (error.retryable and fallback and fallback_provider):
                raise
            try:
                value, attempts = await self._invoke(
                    stage=stage, provider=fallback_provider, operation=fallback, trace_id=trace_id,
                    model_name=fallback_model, owner_user_id=effective_owner_user_id,
                )
            except AIExecutionError as fallback_error:
                raise AIExecutionError(
                    fallback_error.code,
                    f"{fallback_error}; xử lý thất bại trên cả 2 nhà cung cấp",
                    retryable=fallback_error.retryable,
                ) from fallback_error
            logger.warning(
                "ai_execution_fallback=%s",
                json.dumps(
                    {"trace_id": trace_id, "stage": stage.value, "provider": fallback_provider}
                ),
            )
            return AIExecutionResult(value, trace_id, fallback_provider, attempts, True)

    @staticmethod
    def _record(
        trace_id: str,
        stage: AIStage,
        provider: Provider,
        attempt: int,
        outcome: str,
        started: float,
        *,
        model_name: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "ai_execution=%s",
            json.dumps(
                {
                    "trace_id": trace_id,
                    "stage": stage.value,
                    "provider": provider,
                    "model": model_name,
                    "attempt": attempt,
                    "outcome": outcome,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "estimated_cost_usd": cost_usd,
                    "cache_outcome": "bypass",
                    "latency_ms": duration_ms,
                }
            ),
        )
        try:
            global _llmops_tracer
            if _llmops_tracer is None:
                _llmops_tracer = LLMOpsTracer()
            _llmops_tracer.record_span(
                session_id=trace_id,
                component_name=f"ai.{stage.value}.{provider}",
                model_name=model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                duration_ms=duration_ms,
                status=outcome.upper(),
                metadata={"stage": stage.value, "provider": provider},
            )
        except Exception:
            # Observability must never change the provider result or retry path.
            logger.warning("LLMOps span recording failed")


_executor: AIExecutor | None = None
_last_trace_id: ContextVar[str | None] = ContextVar("ai_last_trace_id", default=None)
_current_owner_user_id: ContextVar[int | None] = ContextVar("ai_owner_user_id", default=None)


def get_last_ai_trace_id() -> str | None:
    """Return the current task's latest metadata-only provider trace id."""
    return _last_trace_id.get()


def bind_ai_owner(owner_user_id: int):
    """Bind an authenticated owner for per-user usage accounting."""
    return _current_owner_user_id.set(owner_user_id)


def reset_ai_owner(token) -> None:
    _current_owner_user_id.reset(token)


def get_ai_executor() -> AIExecutor:
    global _executor
    if _executor is None:
        _executor = AIExecutor()
    return _executor
