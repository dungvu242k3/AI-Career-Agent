"""High-Concurrency Stress & Load Testing Suite.

Simulates 50, 100, and 200 concurrent virtual users hitting core REST API endpoints
simultaneously, validating 0% error rate and measuring concurrency throughput.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from httpx import AsyncClient, ASGITransport
from be.main import app


async def simulate_user_session(client: AsyncClient, user_idx: int) -> dict[str, any]:
    """Simulate a realistic user flow across endpoints."""
    t0 = time.perf_counter()
    errors = 0
    requests_made = 0

    # 1. Health check
    try:
        r1 = await client.get("/health")
        requests_made += 1
        if r1.status_code != 200:
            errors += 1
    except Exception:
        errors += 1

    # 2. Query jobs by domain (Hybrid Search)
    try:
        r2 = await client.get("/api/v1/jobs/by-domain?domain=backend&limit=5")
        requests_made += 1
        if r2.status_code != 200:
            errors += 1
    except Exception:
        errors += 1

    # 3. Chat Job Search Intent
    try:
        r3 = await client.post(
            "/api/v1/chat/message",
            json={"message": "Tìm việc Senior Python Backend tại Hà Nội", "candidate_id": None},
        )
        requests_made += 1
        if r3.status_code != 200:
            errors += 1
    except Exception:
        errors += 1

    duration_ms = (time.perf_counter() - t0) * 1000.0
    return {
        "user_idx": user_idx,
        "requests_made": requests_made,
        "errors": errors,
        "duration_ms": duration_ms,
    }


async def run_concurrency_test(virtual_users: int = 100) -> dict[str, any]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        start_time = time.perf_counter()
        tasks = [simulate_user_session(client, i) for i in range(virtual_users)]
        results = await asyncio.gather(*tasks)
        total_time_s = time.perf_counter() - start_time

    total_requests = sum(r["requests_made"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    durations = [r["duration_ms"] for r in results]
    durations.sort()

    rps = total_requests / total_time_s if total_time_s > 0 else 0
    error_rate = (total_errors / total_requests) * 100.0 if total_requests > 0 else 0

    return {
        "vus": virtual_users,
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate": error_rate,
        "total_time_s": total_time_s,
        "rps": rps,
        "p50_ms": durations[int(len(durations) * 0.50)],
        "p95_ms": durations[int(len(durations) * 0.95)],
        "p99_ms": durations[int(len(durations) * 0.99)],
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=" * 80)
    print(" [LOAD TEST] HIGH-CONCURRENCY ASYNC LOAD TESTING SUITE ")
    print(" [TARGET] Endpoints: /health, /jobs/by-domain, /chat/message")
    print("=" * 80)

    stages = [50, 100, 200]
    all_passed = True

    print(f"\n{'VUs':<6} | {'TOTAL REQS':<12} | {'ERRORS':<8} | {'ERROR RATE':<12} | {'P95 LATENCY':<14} | {'THROUGHPUT':<14} | {'STATUS'}")
    print("-" * 88)

    for vus in stages:
        stats = asyncio.run(run_concurrency_test(vus))
        is_pass = stats["error_rate"] == 0.0 and stats["p95_ms"] < 2500.0
        if not is_pass:
            all_passed = False

        status_str = "[PASS]" if is_pass else "[FAIL]"
        print(
            f"{stats['vus']:<6} | {stats['total_requests']:<12} | {stats['total_errors']:<8} | "
            f"{stats['error_rate']:>5.2f}%       | {stats['p95_ms']:>8.2f} ms     | "
            f"{stats['rps']:>7.1f} req/s     | {status_str}"
        )

    print("=" * 88)
    if all_passed:
        print("[SUCCESS] CONCURRENCY LOAD TEST COMPLETED WITH 0.00% ERROR RATE! \n")
        return 0
    else:
        print("[WARNING] HIGH-CONCURRENCY TEST DETECTED ERRORS OR EXCESSIVE LATENCY.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
