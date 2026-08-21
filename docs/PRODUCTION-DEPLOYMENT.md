# Production deployment checklist

1. Deploy Node.js auth and FastAPI with the same `JWT_SECRET`, `JWT_ISSUER`, and `JWT_AUDIENCE`; use different `REFRESH_SECRET` for the auth service only.
2. Set `APP_ENV=production`, `CAREERPILOT_DEBUG=false`, TLS database URL, `rediss://` Redis, `MINIO_SECURE=true`, non-default object-storage credentials, and explicit HTTPS `CORS_ORIGINS`.
3. Put FastAPI, Postgres, Redis, and MinIO on private networking. Only publish the reverse proxy; do not expose the database, MinIO API, or MinIO console.
4. Set `TRUST_PROXY_HOPS` only to the exact number of trusted reverse proxies in front of Node.js. Configure FastAPI `TRUSTED_PROXIES` with those proxy addresses.
5. Pin container images to approved immutable tags or digests and inject secrets through the platform secret manager, never `.env` files.
6. Keep `DATABASE_AUTO_MIGRATE=false` in production. Run `python -m be.db.migrate` as an explicit release step before starting the new application version.
7. Use `docker-compose.production.yml` only with image tags/digests and secrets injected by the deployment platform; its published port is intended to sit behind an external TLS/WAF reverse proxy.

## Database migration release step

The application validates the schema version during production startup but does
not execute schema-changing DDL. The deployment pipeline must:

1. Back up the database and verify the backup reference.
2. Run `python -m be.db.migrate` for the backend schema.
3. Run `npm run migrate:prod` in the built `auth-service` image for the auth schema.
4. Verify both reported `schema_version` values are the versions expected by the release.
5. Start the API and worker containers.
6. Confirm readiness and smoke-test the critical flows.

If migration fails, stop the rollout and keep the previous application version
running. Do not bypass the migration gate by enabling automatic startup DDL in
production.

## AI pipeline production gate

- Configure the canonical routing contract: `AI_PROVIDER`, provider model names,
  `ENABLE_FALLBACK`, token/cost limits, and both provider credentials when
  fallback is enabled. Startup rejects an incomplete production configuration.
- Run a Celery worker **and Celery Beat**. Workers receive only an `ai_jobs.id`;
  the reconciler re-dispatches durable queued jobs after a broker outage.
- Use `POST /api/v1/ai-jobs/cv-ingestion` and
  `POST /api/v1/ai-jobs/cv-generation` for the asynchronous flow. Both return
  `202 { job_id, status, poll_url }`; poll `GET /api/v1/ai-jobs/{job_id}` as
  the owning user. Keep the legacy synchronous endpoints only during rollback.
- Treat `AI_INPUT_REJECTED`, `AI_TIMEOUT`, `AI_PROVIDER_UNAVAILABLE`, and
  `AI_BUDGET_EXCEEDED` as stable client error codes. Do not retry rejected,
  validation, or safety failures.
- Prompts, raw CV text, and PII must never be sent to logs/traces. CV
  extraction/generation caching is disabled. If using the optional response
  cache, set `AI_CACHE_HMAC_SECRET`; it is owner-scoped, HMAC-keyed,
  de-identified, and limited to five minutes.
- Dashboards/alerts should consume `ai_execution` JSON logs by stage/provider:
  alert on provider error/fallback rate, p95 latency, grounding violations, and
  daily token/cost budget exhaustion. Logs expose only metadata and token/cost
  counters.

## Rollout

1. Deploy with the job APIs enabled but route the UI through the legacy sync
   endpoints; shadow a small internal set of requests and compare grounding
   reports, latency, token use, and rendered output.
2. Enable the job flow for 5%, then 25%, then 100% of authenticated users.
   Halt promotion if grounding violations are non-zero or fallback/error/cost
   rates exceed the agreed baseline.
3. Keep synchronous endpoints available for one release window as a rollback
   path. Deprecate them only after the queue, reconciler, alerts, and storage
   cleanup have operated reliably at 100% traffic.

For the release-manager procedure and the distinction between a real canary
and a single-host replacement, see [CANARY-ROLLBACK.md](CANARY-ROLLBACK.md).
For the runtime-platform decision, see
[KUBERNETES-DECISION.md](KUBERNETES-DECISION.md).

## Decision boundary for job matching

The in-repository token-hash vectors are lexical discovery hints, not semantic
embeddings and not consequential scores. They must not be used for ATS,
eligibility, ranking candidates, or hiring decisions. Replace them with a real
embedding service only after a documented offline quality benchmark.

## Ownership migration

The ownership hardening adds `owner_user_id` to candidates, uploads, and analyses. Existing records are assigned owner `0`, which cannot be represented by a valid JWT and is intentionally inaccessible. Re-ingest legacy CVs or run a reviewed, one-time administrator migration that maps every legacy candidate to its real auth-service user before production cutover.
