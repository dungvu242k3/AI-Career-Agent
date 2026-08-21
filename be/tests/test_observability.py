import json
import logging
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import be.main as main_module
from be.main import app
from be.observability import request_metrics
from be.observability import JsonLogFormatter


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_liveness_returns_request_id_and_preserves_safe_input(client):
    response = client.get("/health/live", headers={"X-Request-ID": "test-request-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"
    assert response.json()["status"] == "ok"


def test_invalid_request_id_is_replaced(client):
    response = client.get("/health/live", headers={"X-Request-ID": "contains spaces"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "contains spaces"
    assert len(response.headers["X-Request-ID"]) == 32


def test_valid_w3c_traceparent_is_correlated(client):
    trace_id = "0123456789abcdef0123456789abcdef"
    response = client.get(
        "/health/live",
        headers={"traceparent": f"00-{trace_id}-0123456789abcdef-01"},
    )

    assert response.status_code == 200
    assert response.headers["X-Trace-ID"] == trace_id


def test_readiness_reports_dependency_status(monkeypatch, client):
    monkeypatch.setattr(
        main_module, "check_database_ready", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(main_module, "check_redis_ready", AsyncMock(return_value=True))

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "app": "CareerPilot AI",
        "checks": {"database": True, "redis": True},
    }


def test_readiness_returns_503_when_dependency_is_down(monkeypatch, client):
    monkeypatch.setattr(
        main_module, "check_database_ready", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(main_module, "check_redis_ready", AsyncMock(return_value=False))

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["checks"] == {"database": True, "redis": False}


def test_metrics_expose_request_counters(client):
    request_metrics.reset()
    client.get("/health/live")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "careerpilot_http_requests_total" in response.text
    assert 'method="GET",status_code="200"' in response.text


def test_json_log_formatter_emits_stable_fields():
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request completed",
        args=(),
        exc_info=None,
    )

    payload = json.loads(JsonLogFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "test"
    assert payload["message"] == "request completed"
    assert "timestamp" in payload
