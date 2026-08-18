"""Enterprise LLMOps Distributed Tracing & Token Cost Budgeting Engine.

Provides real-time tracking of:
1. Agent Tool Spans & Latency
2. Prompt & Completion Token Counting
3. Real-time USD Cost Attribution
4. Session Cost Budget Quotas & Overuse Prevention
"""

import time
import uuid
from typing import Any
from pydantic import BaseModel, Field


class LLMSpan(BaseModel):
    """Individual span representing an LLM or Agent tool execution."""

    span_id: str = Field(default_factory=lambda: f"span-{uuid.uuid4().hex[:8]}")
    session_id: str
    component_name: str
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    duration_ms: float = 0.0
    status: str = "SUCCESS"
    timestamp: float = Field(default_factory=time.time)


class SessionMetrics(BaseModel):
    """Aggregated token and cost metrics for a user session."""

    session_id: str
    total_spans: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    budget_limit_usd: float = 0.50  # Default $0.50 max budget per session
    is_budget_exceeded: bool = False


# Standard Model Pricing per 1 Million Tokens (USD)
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "deepseek-v3": {"input": 0.14, "output": 0.28},
    "local-embeddings": {"input": 0.00, "output": 0.00},
}


class LLMOpsTracer:
    """Enterprise In-Memory & OpenTelemetry-Ready LLMOps Tracer."""

    def __init__(self, default_budget_usd: float = 0.50):
        self.default_budget_usd = default_budget_usd
        self._spans: list[LLMSpan] = []
        self._session_costs: dict[str, float] = {}
        self._session_tokens: dict[str, int] = {}

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Compute exact USD cost based on token counts and model pricing."""
        rates = MODEL_PRICING.get(model.lower(), MODEL_PRICING["gpt-4o-mini"])
        cost_in = (prompt_tokens / 1_000_000.0) * rates["input"]
        cost_out = (completion_tokens / 1_000_000.0) * rates["output"]
        return round(cost_in + cost_out, 6)

    def record_span(
        self,
        session_id: str,
        component_name: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration_ms: float,
        status: str = "SUCCESS",
    ) -> LLMSpan:
        """Record an execution span and update session budget meters."""
        cost = self.calculate_cost(model_name, prompt_tokens, completion_tokens)
        total_tokens = prompt_tokens + completion_tokens

        span = LLMSpan(
            session_id=session_id,
            component_name=component_name,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=cost,
            duration_ms=duration_ms,
            status=status,
        )

        self._spans.append(span)
        self._session_costs[session_id] = self._session_costs.get(session_id, 0.0) + cost
        self._session_tokens[session_id] = self._session_tokens.get(session_id, 0) + total_tokens

        return span

    def is_budget_exceeded(self, session_id: str, budget_limit_usd: float | None = None) -> bool:
        """Check if user session has exceeded allocated USD cost quota."""
        limit = budget_limit_usd or self.default_budget_usd
        current_cost = self._session_costs.get(session_id, 0.0)
        return current_cost >= limit

    def get_session_metrics(self, session_id: str, budget_limit_usd: float | None = None) -> SessionMetrics:
        """Retrieve aggregated metrics for session dashboard."""
        limit = budget_limit_usd or self.default_budget_usd
        session_spans = [s for s in self._spans if s.session_id == session_id]
        total_tokens = self._session_tokens.get(session_id, 0)
        total_cost = self._session_costs.get(session_id, 0.0)

        return SessionMetrics(
            session_id=session_id,
            total_spans=len(session_spans),
            total_tokens=total_tokens,
            total_cost_usd=round(total_cost, 6),
            budget_limit_usd=limit,
            is_budget_exceeded=total_cost >= limit,
        )
