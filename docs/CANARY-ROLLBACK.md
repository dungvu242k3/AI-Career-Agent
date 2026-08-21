# Canary and rollback runbook

This runbook starts only after the release image digests have passed CI and the
manual staging verification workflow. It applies to the backend, Auth service,
worker, Beat, and frontend as one release unit.

## Preconditions

1. Record the candidate and previous image digests, migration versions, change
   owner, approval, and planned rollback owner in the release ticket.
2. Confirm a tested database backup exists and record its restore reference.
3. Confirm all database migrations are backward-compatible with the previous
   application version. Application image rollback is normal; automatic schema
   downgrade is prohibited.
4. Define the baseline and stop thresholds before traffic is changed: HTTP 5xx
   rate, readiness failures, p95 latency, queue age, AI job failure/fallback
   rate, and token/cost rate. Do not choose thresholds while an incident is in
   progress.
5. Verify that dashboards can correlate frontend/API requests, workers, and AI
   jobs by request or trace ID without exposing prompts, CV text, tokens, or
   credentials.

## Choose the correct rollout shape

| Deployment shape | Safe rollout method | Limitation |
| --- | --- | --- |
| Single Docker Compose host | Blue/green host or internal-canary endpoint, then a whole-release switch | Compose alone cannot split 5%/25% user traffic between two versions. |
| Two or more hosts behind a load balancer | Weighted target groups: 1%, 5%, 25%, 50%, 100% | The load balancer must have health-based removal and an explicit rollback route. |
| Kubernetes with a rollout controller | Canary steps through Deployment/Argo Rollouts plus readiness gates | Requires cluster operations, policy, and observability ownership. |

Never label a full replacement on one Compose host as a percentage canary. If
traffic splitting is unavailable, treat the rollout as blue/green and use a
separate canary target for internal users first.

## Canary loop

For every traffic step, keep the candidate active long enough to observe normal
request and background-job behavior (minimum 15 minutes and one worker retry
window). At each step:

1. Run the smoke check and verify all readiness checks are healthy.
2. Inspect the dashboard against the pre-release baseline.
3. Exercise one authenticated staging-like user path; do not use real customer
   CVs for a release check.
4. Check queue depth/age, worker retries, provider fallback, error codes, and
   cost counters.
5. Promote only when every agreed stop threshold remains within bounds.

Stop promotion immediately on a readiness failure, cross-user data exposure,
unexpected migration behavior, sustained 5xx increase, queue growth, or an AI
provider/cost alert. Preserve trace IDs and aggregate metrics for diagnosis;
do not copy PII into the incident record.

## Rollback

1. Freeze promotion and route new traffic to the previous healthy image
   digests, or remove the canary target from the load balancer.
2. Keep the failed version's logs, traces, container identifiers, and metric
   window available for investigation.
3. Redeploy the previous backend, Auth, worker, Beat, and frontend digests as a
   compatible release unit. Do not automatically revert the database schema.
4. Verify live and ready endpoints, the manual smoke workflow, Auth-to-backend
   token validation, and queue reconciliation after rollback.
5. Record actual rollback time, customer impact, queued job outcome, and any
   required compensating migration before reopening promotion.

## Rehearsal cadence

Rehearse this in staging before the first production launch and after any
destructive or non-backward-compatible operational change. A rehearsal must
prove that the previous image can start against the current schema, a worker
can resume queued jobs, alerts fire, and the rollback owner can complete the
procedure within the stated recovery-time objective.
