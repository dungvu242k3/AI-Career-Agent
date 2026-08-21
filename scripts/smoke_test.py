"""Small dependency-free staging smoke test.

Environment variables:
  FRONTEND_URL  public frontend URL, default http://127.0.0.1:8080
  BACKEND_URL   internal/backend URL, default http://127.0.0.1:8000
  AUTH_URL      internal/auth URL, default http://127.0.0.1:4000
"""

from __future__ import annotations

import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check(name: str, base_url: str, path: str, *, require_trace: bool = False) -> None:
    url = f"{base_url.rstrip('/')}{path}"
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}: {body[:200]}")
            if require_trace and not response.headers.get("X-Trace-ID"):
                raise RuntimeError("X-Trace-ID header is missing")
    except HTTPError as error:
        body = error.read(4096).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {body[:200]}") from error
    except URLError as error:
        raise RuntimeError(str(error.reason)) from error
    print(f"PASS {name}: {url}")


def main() -> int:
    checks = (
        ("frontend", os.getenv("FRONTEND_URL", "http://127.0.0.1:8080"), "/"),
        (
            "backend-live",
            os.getenv("BACKEND_URL", "http://127.0.0.1:8000"),
            "/health/live",
        ),
        (
            "backend-ready",
            os.getenv("BACKEND_URL", "http://127.0.0.1:8000"),
            "/health/ready",
        ),
        (
            "backend-metrics",
            os.getenv("BACKEND_URL", "http://127.0.0.1:8000"),
            "/metrics",
        ),
        ("auth-live", os.getenv("AUTH_URL", "http://127.0.0.1:4000"), "/health/live"),
        ("auth-ready", os.getenv("AUTH_URL", "http://127.0.0.1:4000"), "/health/ready"),
    )
    try:
        for name, base_url, path in checks:
            check(name, base_url, path, require_trace=name == "backend-live")
    except RuntimeError as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
