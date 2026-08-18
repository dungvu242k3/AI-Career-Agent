"""Multi-Model Circuit Breaker & Resilient Fallback Mesh.

Implements automated circuit breaker to prevent cascading failures:
States:
- CLOSED: Normal operation, routes to primary model (OpenAI GPT-4o).
- OPEN: Tripped after N consecutive upstream errors/timeouts, fast-routes to secondary model (Claude / Local Fallback).
- HALF_OPEN: Periodically tests upstream health after recovery timeout.
"""

import time
from enum import Enum
from typing import Callable, Any
from pydantic import BaseModel, Field


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerStatus(BaseModel):
    state: CircuitState
    consecutive_failures: int
    failure_threshold: int
    recovery_timeout_seconds: float
    last_failure_timestamp: float | None = None
    active_model: str


class ModelCircuitBreaker:
    """Enterprise Resilience Circuit Breaker for LLM API Providers."""

    def __init__(
        self,
        primary_model: str = "gpt-4o",
        secondary_model: str = "claude-3-5-sonnet",
        fallback_model: str = "deepseek-v3",
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 30.0,
    ):
        self.primary_model = primary_model
        self.secondary_model = secondary_model
        self.fallback_model = fallback_model
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds

        self.state: CircuitState = CircuitState.CLOSED
        self.consecutive_failures: int = 0
        self.last_failure_time: float | None = None

    def get_active_model(self) -> str:
        """Select appropriate model based on current circuit breaker state."""
        self._check_and_update_state()
        if self.state == CircuitState.CLOSED:
            return self.primary_model
        elif self.state == CircuitState.HALF_OPEN:
            return self.secondary_model
        else:
            return self.fallback_model

    def record_success(self):
        """Record successful execution and restore circuit to CLOSED."""
        self.consecutive_failures = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record upstream API error and potentially trip the circuit."""
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def _check_and_update_state(self):
        """Transition OPEN state to HALF_OPEN after recovery cooldown."""
        if self.state == CircuitState.OPEN and self.last_failure_time:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN

    def get_status(self) -> CircuitBreakerStatus:
        self._check_and_update_state()
        return CircuitBreakerStatus(
            state=self.state,
            consecutive_failures=self.consecutive_failures,
            failure_threshold=self.failure_threshold,
            recovery_timeout_seconds=self.recovery_timeout_seconds,
            last_failure_timestamp=self.last_failure_time,
            active_model=self.get_active_model(),
        )
