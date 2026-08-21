from be.telemetry import (
    configure_api_telemetry,
    configure_worker_telemetry,
    shutdown_telemetry,
)


def test_telemetry_is_optional_when_no_endpoint_is_configured(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    assert configure_api_telemetry(object()) is False
    assert configure_worker_telemetry() is False
    shutdown_telemetry()
