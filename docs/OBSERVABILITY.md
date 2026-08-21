# Observability contract

The backend exposes a small, dependency-light observability contract that can
be used immediately by a reverse proxy, container platform, or Prometheus
scraper.

## Endpoints

- `GET /health/live` checks only that the process can serve requests.
- `GET /health/ready` checks the configured database and Redis dependencies and
  returns `503` while the service must not receive traffic.
- `GET /metrics` exposes request counters and duration sums in Prometheus text
  format. Keep this endpoint private at the proxy/network layer.
- `GET /health` remains as a backward-compatible liveness endpoint.

## Correlation

Every response receives `X-Request-ID` and `X-Trace-ID`. A safe incoming
`X-Request-ID` is preserved; otherwise a new ID is generated. A valid W3C
`traceparent` header preserves its trace ID. The IDs are available through
request context and are included in request-completion logs.

The current metrics intentionally do not label raw URLs. UUIDs, file keys, and
user-controlled paths would create unbounded metric cardinality. Route-level
distributed spans are exported only when the optional OpenTelemetry endpoint is
configured.

AI execution now records metadata-only LLMOps spans at the provider execution
boundary. These spans include stage, provider, model, attempt, latency, token
counts, and estimated cost. Recording failures are intentionally non-blocking.

## Logging

Set `LOG_FORMAT=json` locally when testing log collection. Production enables
the JSON formatter automatically. Request logs contain metadata only; raw CV
text, prompts, tokens, and credentials must not be logged.

The process-local metrics are a bootstrap contract, not a replacement for a
multi-replica metrics backend. Before horizontal scaling, connect the same
request/trace contract to OpenTelemetry and an external metrics collector.

The production image includes optional OpenTelemetry instrumentation. Set
`OTEL_EXPORTER_OTLP_ENDPOINT` and, when needed,
`OTEL_EXPORTER_OTLP_HEADERS` to enable FastAPI, HTTPX, Redis, and Celery span
export. Leave the endpoint empty in local development. Exporter failures must
never fail an API request or AI job.
