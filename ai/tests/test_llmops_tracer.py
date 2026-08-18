"""Unit tests for LLMOpsTracer and Token Cost Budgeting."""

import pytest
from ai.llmops.tracer import LLMOpsTracer


def test_tracer_records_spans_and_calculates_cost():
    """Verify span tracking and token pricing math."""
    tracer = LLMOpsTracer(default_budget_usd=0.10)
    session_id = "test-session-001"

    span = tracer.record_span(
        session_id=session_id,
        component_name="CVTailorActor",
        model_name="gpt-4o-mini",
        prompt_tokens=10_000,
        completion_tokens=2_000,
        duration_ms=450.0,
    )

    assert span.total_tokens == 12_000
    assert span.estimated_cost_usd > 0.0
    assert not tracer.is_budget_exceeded(session_id)


def test_tracer_enforces_budget_limits():
    """Verify that exceeding token budget triggers budget alert."""
    tracer = LLMOpsTracer(default_budget_usd=0.01)
    session_id = "test-session-heavy"

    # Record large GPT-4o usage exceeding budget limit
    tracer.record_span(
        session_id=session_id,
        component_name="HeavyEvaluation",
        model_name="gpt-4o",
        prompt_tokens=50_000,
        completion_tokens=10_000,
        duration_ms=1200.0,
    )

    metrics = tracer.get_session_metrics(session_id)
    assert metrics.is_budget_exceeded
    assert tracer.is_budget_exceeded(session_id)
