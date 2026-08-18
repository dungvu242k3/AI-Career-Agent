"""Enterprise One-Click Production Release Verification Suite.

Runs end-to-end checks across:
1. Static AST Security Scanner
2. Latency Percentiles & SLA Benchmark Suite
3. High-Concurrency Load Testing
4. Memory Profiling & Resource Leak Detection
5. Pytest Full Test Suite (AI Core + Backend Routers)
6. Frontend Production Bundle Build
"""

import os
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent


def run_step(step_name: str, cmd: list[str], cwd: Path | None = None) -> tuple[bool, str, float]:
    t0 = time.perf_counter()
    target_cwd = cwd or WORKSPACE_ROOT
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(target_cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        duration = time.perf_counter() - t0
        output = proc.stdout + "\n" + proc.stderr
        is_success = proc.returncode == 0
        return is_success, output, duration
    except Exception as e:
        duration = time.perf_counter() - t0
        return False, str(e), duration


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=" * 80)
    print(" 🚀 ENTERPRISE MASTER PRODUCTION RELEASE VERIFICATION SUITE ")
    print(f" [TARGET WORKSPACE] {WORKSPACE_ROOT}")
    print("=" * 80)

    steps = [
        ("1. AST Static Security Scanner", [sys.executable, ".agent/scripts/security_scanner.py", "."], WORKSPACE_ROOT),
        ("2. AI Latency Percentile Benchmark", [sys.executable, ".agent/scripts/benchmark_engine.py", "1000"], WORKSPACE_ROOT),
        ("3. High-Concurrency Load Testing", [sys.executable, ".agent/scripts/load_test.py"], WORKSPACE_ROOT),
        ("4. Memory & Leak Profiler", [sys.executable, ".agent/scripts/profile_memory.py"], WORKSPACE_ROOT),
        ("5. Pytest Full Backend & AI Suite", [str(WORKSPACE_ROOT / "be" / ".venv" / "Scripts" / "python.exe"), "-m", "pytest"], WORKSPACE_ROOT),
        ("6. Frontend Production Bundle Build", ["npm.cmd" if os.name == "nt" else "npm", "run", "build"], WORKSPACE_ROOT / "fe"),
    ]

    all_passed = True
    summary_table = []

    for name, cmd, cwd in steps:
        print(f"\n▶ Executing: {name} ...", flush=True)
        success, output, elapsed = run_step(name, cmd, cwd)
        status_str = "[PASS]" if success else "[FAIL]"
        summary_table.append((name, status_str, elapsed))
        if not success:
            all_passed = False
            print(f"❌ {name} FAILED after {elapsed:.2f}s:")
            print("-" * 60)
            print(output.strip()[-800:])
            print("-" * 60)
        else:
            print(f"✅ {name} PASSED ({elapsed:.2f}s)")

    print("\n" + "=" * 80)
    print(" 📋 MASTER VERIFICATION SUMMARY DASHBOARD ")
    print("=" * 80)
    print(f"{'VERIFICATION STEP':<45} | {'STATUS':<10} | {'DURATION':<10}")
    print("-" * 72)
    for name, st, dur in summary_table:
        print(f"{name:<45} | {st:<10} | {dur:>6.2f}s")
    print("=" * 72)

    if all_passed:
        print("\n🎉 ALL 6 PRODUCTION CHECKS PASSED 100%! SYSTEM IS PRODUCTION READY! 🚀\n")
        return 0
    else:
        print("\n⚠️ ONE OR MORE CHECKS FAILED. PLEASE REVIEW LOGS ABOVE.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
