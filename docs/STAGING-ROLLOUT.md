# Staging rollout runbook

This runbook is for the image-based staging deployment described by
`docker-compose.production.yml`. It assumes PostgreSQL, Redis, object storage,
an OTLP collector, and a TLS/reverse proxy are reachable on private networks.

## Release preparation

1. Merge only after the required CI checks are green.
2. Create a version tag, for example `v0.1.0-rc.1`, or manually run the
   `Release container images` workflow with an immutable `image_tag`.
3. Record the three published image references and their digests.
4. Prepare the staging environment file in the secret manager. It must include
   the required Compose variables; never commit this file.
5. Set `BACKEND_IMAGE`, `AUTH_IMAGE`, and `FRONTEND_IMAGE` to the exact image
   digests, not a mutable `latest` tag.

## Deployment order

Run these steps from the staging deployment host:

1. Verify database backup and connectivity.
2. Run the backend migration image:

   `docker run --rm --env-file staging.env "$BACKEND_IMAGE" python -m be.db.migrate`

3. Run the Auth migration image:

   `docker run --rm --env-file staging.env "$AUTH_IMAGE" npm run migrate:prod`

4. Render the Compose configuration and confirm only the frontend port is
   published:

   `docker compose --env-file staging.env -f docker-compose.production.yml config`

5. Start the stack:

   `docker compose --env-file staging.env -f docker-compose.production.yml up -d`

6. Confirm service state and logs:

   `docker compose --env-file staging.env -f docker-compose.production.yml ps`

## Smoke checks

Verify, through the TLS reverse proxy:

- Frontend loads and SPA refresh works.
- Auth `/health/live` returns 200.
- Backend `/health/live` returns 200 with `X-Request-ID` and `X-Trace-ID`.
- Backend `/health/ready` returns 200.
- Backend `/metrics` is not publicly accessible unless explicitly protected.
- Register/login/refresh works with a staging test user.
- User A cannot read User B's candidate, upload, analysis, or AI job.
- CV ingestion returns `202` and eventually reaches a terminal job state.
- Worker retry and Beat reconciliation are visible in logs/metrics.
- No prompt, raw CV, token, or credential appears in logs/traces.

The repeatable dependency-free check is:

`python scripts/smoke_test.py`

Set `FRONTEND_URL`, `BACKEND_URL`, and `AUTH_URL` when the services are not on
the local ports used by the default values.

## Repeatable staging verification

Use **Staging verification** from GitHub Actions only after the release is
healthy. It is deliberately a manual workflow and allows only `staging` or
`preproduction`, never production. Supply URLs that the GitHub runner can
reach; use a self-hosted runner in the private network if those services are
not public.

The workflow has three independent, bounded checks:

- Smoke: public frontend plus backend/Auth liveness, readiness, metrics, and
  backend trace propagation.
- Auth/ownership E2E: opt-in only. It creates one disposable user and checks
  that an Auth-issued JWT is accepted by the backend and malformed tokens are
  rejected. With **run async job** enabled it creates a second user and also
  checks job idempotency and cross-user `404` isolation.
- k6 load: default 5 virtual users for 30 seconds against backend health. It
  fails at p95 >= 500 ms, error rate >= 1%, or absent trace headers. Tune those
  thresholds only after documenting the agreed staging SLO.

The E2E flow must target a disposable staging database with a test-data
retention/cleanup policy. Async job verification can reach an AI worker and
provider, so run it only with a test provider, bounded budget, and explicit
operator approval. The k6 profile intentionally never calls AI or authenticated
business endpoints; create a separate reviewed profile before load-testing
upload or generation paths.

## Rollback

1. Stop promotion if readiness, authorization, queue age, error rate, or AI
   cost violates the staging baseline.
2. Keep the migration applied if it is backward-compatible.
3. Set the three image variables back to the previous digests.
4. Run `docker compose ... up -d` and verify the previous release.
5. Do not downgrade schema automatically. Use a reviewed compensating
   migration only if the database change is not backward-compatible.
