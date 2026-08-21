# Engineering quality gates

This document defines the staged quality bar for CareerPilot AI. The repository
currently contains a large set of uncommitted changes, so formatting and lint
cleanup must be handled in small, reviewable batches rather than by reformatting
the whole tree in one operation.

## Current baseline

The first CI gate runs:

- `python -m pytest -q`
- `npm test` in `auth-service` (typecheck, build, and JWT unit tests)
- `npm run lint` in `fe`
- `npm run build` in `fe`
- `python -m be.db.migrate` against an isolated SQLite database
- `pip-audit` for both backend runtime and development dependencies
- `npm audit --package-lock-only --audit-level=high` for Auth and frontend
- production image builds for backend, Auth, and frontend

The current local baseline is 141 passing Python tests, passing Auth tests,
a successful frontend production build, and clean dependency audits. Backend
production images install only `be/requirements.txt`; test tooling lives in
`be/requirements-dev.txt` and is excluded from release images.

Ruff currently reports existing issues in the Python tree. It is intentionally
tracked as a follow-up gate instead of being auto-fixed across files that may
contain unrelated in-progress work.

## Pull request rules

Every pull request must:

1. Have one focused purpose.
2. Include a test for new behavior or a regression test for a bug fix.
3. Preserve authorization and owner isolation.
4. Avoid secrets, prompts, raw CV text, and PII in logs or fixtures.
5. Explain database migration, rollout, and rollback impact.
6. Keep external provider calls mockable in unit tests.
7. Pass all required CI checks before merge.

Security, authentication, ownership, migration, AI cost, and deployment
changes require an additional reviewer familiar with that area.

## Test layers

### Unit tests

Unit tests must be deterministic and must not call real AI providers, databases,
Redis, object storage, or the network. Use fakes or mocks for those boundaries.
They cover parsing, validation, authorization, rate limits, retry decisions,
cost budgets, circuit breakers, job state transitions, and error mapping.

### Integration tests

Integration tests use isolated PostgreSQL, Redis, and object-storage instances.
They cover migrations, API/database behavior, worker persistence, idempotency,
and storage cleanup.

### End-to-end tests

End-to-end tests cover the critical user flow: authenticate, upload a CV, create
an asynchronous AI job, poll it, retrieve the result, and verify that another
user cannot access it.

## Clean-code follow-up

The Python lint/format debt will be handled by bounded changes:

1. Add the formatter/linter configuration.
2. Fix one module or bounded package at a time.
3. Run its tests before and after the cleanup.
4. Review the diff for accidental behavior changes.
5. Promote lint from advisory to blocking after the baseline reaches zero.
