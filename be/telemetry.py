"""Optional OpenTelemetry bootstrap for API and worker processes."""

from __future__ import annotations

import logging
import os
from typing import Any


logger = logging.getLogger(__name__)
_provider: Any | None = None
_api_instrumented = False
_worker_instrumented = False


def _endpoint_configured() -> bool:
    return bool(os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip())


def _build_provider() -> Any | None:
    if not _endpoint_configured():
        return None
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning(
            "OpenTelemetry endpoint configured but telemetry packages are unavailable"
        )
        return None

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": os.getenv("OTEL_SERVICE_NAME", "careerpilot-backend"),
                "deployment.environment": os.getenv("APP_ENV", "development"),
            }
        )
    )
    exporter = OTLPSpanExporter(
        endpoint=os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"],
        headers=os.getenv("OTEL_EXPORTER_OTLP_HEADERS", ""),
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider


def configure_api_telemetry(app: Any) -> bool:
    """Instrument FastAPI and supported client libraries when configured."""
    global _api_instrumented, _provider
    if _api_instrumented or not _endpoint_configured():
        return _api_instrumented
    provider = _build_provider()
    if provider is None:
        return False

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls="health,health/live,health/ready,metrics",
        )
        HTTPXClientInstrumentor().instrument()
        RedisInstrumentor().instrument()
    except Exception:
        logger.exception("OpenTelemetry API instrumentation failed")
        provider.shutdown()
        return False

    _provider = provider
    _api_instrumented = True
    logger.info("OpenTelemetry API instrumentation enabled")
    return True


def configure_worker_telemetry() -> bool:
    """Instrument Celery when the worker image includes the optional packages."""
    global _worker_instrumented, _provider
    if _worker_instrumented or not _endpoint_configured():
        return _worker_instrumented
    provider = _build_provider()
    if provider is None:
        return False
    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor

        CeleryInstrumentor().instrument()
    except Exception:
        logger.exception("OpenTelemetry worker instrumentation failed")
        provider.shutdown()
        return False
    _provider = provider
    _worker_instrumented = True
    logger.info("OpenTelemetry worker instrumentation enabled")
    return True


def shutdown_telemetry() -> None:
    """Flush spans during graceful process shutdown."""
    global _provider, _api_instrumented, _worker_instrumented
    if _provider is not None:
        _provider.shutdown()
    _provider = None
    _api_instrumented = False
    _worker_instrumented = False
