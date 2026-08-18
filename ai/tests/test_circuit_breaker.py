"""Unit tests for ModelCircuitBreaker."""

import pytest
from ai.llmops.circuit_breaker import ModelCircuitBreaker, CircuitState


def test_circuit_breaker_trips_to_open_on_threshold():
    """Verify that 3 consecutive failures trip circuit from CLOSED to OPEN."""
    breaker = ModelCircuitBreaker(
        primary_model="gpt-4o",
        secondary_model="claude-3-5-sonnet",
        fallback_model="deepseek-v3",
        failure_threshold=3,
    )

    assert breaker.get_active_model() == "gpt-4o"
    assert breaker.state == CircuitState.CLOSED

    # Simulate 2 failures -> Still CLOSED
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.get_active_model() == "gpt-4o"

    # 3rd failure -> Tripped to OPEN -> Routes to fallback
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    assert breaker.get_active_model() == "deepseek-v3"


def test_circuit_breaker_resets_on_success():
    """Verify that a successful run resets failure counts."""
    breaker = ModelCircuitBreaker(failure_threshold=3)

    breaker.record_failure()
    breaker.record_failure()
    assert breaker.consecutive_failures == 2

    breaker.record_success()
    assert breaker.consecutive_failures == 0
    assert breaker.state == CircuitState.CLOSED
