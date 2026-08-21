## Summary

<!-- What changed and why? Keep this focused on one change. -->

## Change type

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor / clean code
- [ ] Security
- [ ] Database migration
- [ ] Deployment / infrastructure

## Verification

- [ ] Backend/AI tests pass: `python -m pytest -q`
- [ ] Auth tests/typecheck/build pass: `npm test` in `auth-service`
- [ ] Frontend checks pass: `npm run lint` and `npm run build` in `fe`
- [ ] Auth production build passes: `npm run build` in `auth-service`
- [ ] Container images build successfully in CI
- [ ] If deployment-related, staging rollout/rollback steps are documented
- [ ] If deployment-related, `python scripts/smoke_test.py` is documented or run
- [ ] New behavior has unit or integration tests
- [ ] A bug fix includes a regression test

## Production safety

- [ ] No secret, token, prompt, raw CV, or PII was added to logs/tests/fixtures
- [ ] Authorization and cross-user data isolation were reviewed
- [ ] Retry/idempotency behavior was reviewed for external calls or jobs
- [ ] Health checks, logs, metrics, or traces were updated if needed
- [ ] Database migration is backward-compatible and has a rollback plan
- [ ] Rollback impact is understood

## Reviewer notes

<!-- Mention risk, migration steps, rollout plan, or anything requiring special review. -->
