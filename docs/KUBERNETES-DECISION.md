# Kubernetes decision for CareerPilot AI

## Current decision

Kubernetes is **not a prerequisite** for the first production release. The
current Compose production shape is appropriate when the team can operate a
small number of services on one controlled deployment host and relies on
managed PostgreSQL, Redis, object storage, TLS/WAF, backups, and monitoring.

The stronger requirements before launch are immutable images, explicit
migrations, health/readiness, backup/rollback practice, traceable logs and
metrics, CI security gates, and a reachable staging environment. Those are
already useful whether the runtime is Compose or Kubernetes.

## Adopt Kubernetes when the evidence supports it

Start a Kubernetes pilot only when at least three of these conditions are true
and a named owner can operate the cluster:

- High availability requires more than one application host or availability
  zone.
- Backend and worker workloads need independent autoscaling beyond a single
  host.
- Several teams/services need standard deployment, network-policy, and secret
  controls.
- Releases require real traffic-split canaries frequently enough that a
  load-balancer-only solution is no longer manageable.
- The team has on-call capacity for cluster upgrades, node failures, ingress,
  image policy, and incident response.

Do not move solely because the application has containers or a Celery worker;
Kubernetes adds an operational control plane that must be maintained.

## What must exist before a Kubernetes migration

1. Infrastructure as code for network, registry access, DNS/TLS, managed data
   stores, and secret delivery.
2. Separate Deployments for backend, Auth, worker, and Beat; a one-off,
   release-gated migration Job; and no application startup DDL.
3. Liveness/readiness probes, resource requests/limits, horizontal autoscaling
   signals, disruption budgets, and a worker queue-age alert.
4. Private network policies, workload identities, encrypted secrets, and an
   ingress/WAF with rate limiting.
5. Central logs, metrics, traces, dashboard ownership, alert routing, backup
   restoration tests, and an image-signing/scanning policy.
6. A progressive delivery controller or documented weighted-ingress procedure
   for canary and rollback.

Until those prerequisites are funded and owned, improve the existing Compose
deployment with managed data services and a load balancer. That is a valid
production path, not a temporary substitute for operational discipline.
