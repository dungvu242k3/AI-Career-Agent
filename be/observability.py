"""Low-dependency request correlation and Prometheus-compatible metrics."""

from __future__ import annotations

from collections import defaultdict
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import os
import re
from threading import Lock
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)
_request_id_context: ContextVar[str | None] = ContextVar(
    "careerpilot_request_id", default=None
)
_trace_id_context: ContextVar[str | None] = ContextVar(
    "careerpilot_trace_id", default=None
)
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_TRACEPARENT = re.compile(r"^00-([0-9a-f]{32})-[0-9a-f]{16}-0[1-9a-f]$")


class JsonLogFormatter(logging.Formatter):
    """Emit stable, machine-readable fields for a log collector."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = get_request_id()
        trace_id = get_trace_id()
        if request_id:
            payload["request_id"] = request_id
        if trace_id:
            payload["trace_id"] = trace_id
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(*, production: bool = False) -> None:
    """Enable JSON logs in production without changing local developer output."""
    if not production and os.getenv("LOG_FORMAT", "").lower() != "json":
        return
    root = logging.getLogger()
    if any(getattr(handler, "_careerpilot_json", False) for handler in root.handlers):
        return
    handler = logging.StreamHandler()
    handler._careerpilot_json = True
    handler.setFormatter(JsonLogFormatter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def get_request_id() -> str | None:
    """Return the request correlation ID for the current async context."""
    return _request_id_context.get()


def get_trace_id() -> str | None:
    """Return the W3C trace ID for the current async context."""
    return _trace_id_context.get()


def _request_id_from_header(value: str | None) -> str:
    if value and _SAFE_REQUEST_ID.fullmatch(value):
        return value
    return uuid.uuid4().hex


class RequestMetrics:
    """Process-local counters suitable for a first health/metrics gate.

    The metric labels intentionally exclude raw URLs to avoid unbounded
    cardinality from UUIDs, file keys, and user-controlled paths. A later
    OpenTelemetry/Prometheus collector can replace this implementation without
    changing the middleware contract.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: dict[tuple[str, int], int] = defaultdict(int)
        self._duration_sum: dict[tuple[str, int], float] = defaultdict(float)

    def observe(self, method: str, status_code: int, duration_seconds: float) -> None:
        key = (method.upper(), int(status_code))
        with self._lock:
            self._requests[key] += 1
            self._duration_sum[key] += max(0.0, duration_seconds)

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()
            self._duration_sum.clear()

    def prometheus_text(self) -> str:
        with self._lock:
            requests = dict(self._requests)
            durations = dict(self._duration_sum)

        lines = [
            "# HELP careerpilot_http_requests_total Total HTTP requests.",
            "# TYPE careerpilot_http_requests_total counter",
        ]
        for (method, status_code), count in sorted(requests.items()):
            labels = f'method="{method}",status_code="{status_code}"'
            lines.append(f"careerpilot_http_requests_total{{{labels}}} {count}")

        lines.extend(
            [
                "# HELP careerpilot_http_request_duration_seconds_sum HTTP duration sum.",
                "# TYPE careerpilot_http_request_duration_seconds_sum counter",
            ]
        )
        for (method, status_code), duration in sorted(durations.items()):
            labels = f'method="{method}",status_code="{status_code}"'
            lines.append(
                f"careerpilot_http_request_duration_seconds_sum{{{labels}}} {duration:.6f}"
            )
        return "\n".join(lines) + "\n"


request_metrics = RequestMetrics()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a safe request ID and record request duration/status."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = _request_id_from_header(request.headers.get("X-Request-ID"))
        trace_match = _TRACEPARENT.fullmatch(request.headers.get("traceparent", ""))
        trace_id = trace_match.group(1) if trace_match else uuid.uuid4().hex
        request_token = _request_id_context.set(request_id)
        trace_token = _trace_id_context.set(trace_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
            request_metrics.observe(
                request.method,
                response.status_code,
                time.perf_counter() - started,
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Trace-ID"] = trace_id
            logger.info(
                "http_request_completed request_id=%s trace_id=%s method=%s status_code=%s duration_ms=%.2f",
                request_id,
                trace_id,
                request.method,
                response.status_code,
                (time.perf_counter() - started) * 1000,
            )
            return response
        except Exception:
            request_metrics.observe(request.method, 500, time.perf_counter() - started)
            logger.exception(
                "http_request_failed request_id=%s trace_id=%s method=%s",
                request_id,
                trace_id,
                request.method,
            )
            raise
        finally:
            _trace_id_context.reset(trace_token)
            _request_id_context.reset(request_token)
