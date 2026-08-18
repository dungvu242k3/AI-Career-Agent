"""High-performance Sliding Window Rate Limiter for FastAPI.

Protects expensive AI endpoints (CV parsing, LLM generation) from DoS, brute-force,
and token quota exhaustion attacks.
"""

from collections import defaultdict
import logging
import time
from fastapi import HTTPException, Request, status

import os

logger = logging.getLogger(__name__)

# Trusted proxy IP list (can be configured via env var for deployment behind Nginx / Cloudflare)
TRUSTED_PROXIES = set(
    filter(
        None,
        [
            ip.strip()
            for ip in os.getenv("TRUSTED_PROXIES", "127.0.0.1,::1,localhost,testclient").split(",")
        ],
    )
)


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter tracking client IP requests."""

    def __init__(
        self,
        max_requests: int = 5,
        window_seconds: int = 60,
        custom_detail: str | None = None,
        trusted_proxies: set[str] | None = None,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.custom_detail = custom_detail
        self.trusted_proxies = (
            trusted_proxies if trusted_proxies is not None else TRUSTED_PROXIES
        )
        # Storage: ip -> list of unix timestamps
        self._history: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup: float = time.time()

    def reset(self):
        """Clear all rate limit history (useful for test suite isolation)."""
        self._history.clear()

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP with trusted proxy validation to prevent IP spoofing attacks."""
        client_host = request.client.host if request.client else None

        # Only trust X-Forwarded-For if request comes from an authenticated/configured trusted proxy
        if client_host and (client_host in self.trusted_proxies or "*" in self.trusted_proxies):
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                return forwarded.split(",")[0].strip()

        if client_host:
            return client_host

        # Fallback for synthetic requests where request.client is None
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        return "127.0.0.1"

    def _cleanup_stale_entries(self, current_time: float):
        """Periodically purge expired timestamps to prevent memory growth."""
        if current_time - self._last_cleanup < 300:  # Cleanup every 5 minutes
            return

        cutoff = current_time - self.window_seconds
        stale_ips = []
        for ip in list(self._history.keys()):
            timestamps = [t for t in self._history[ip] if t > cutoff]
            if timestamps:
                self._history[ip] = timestamps
            else:
                stale_ips.append(ip)

        for ip in stale_ips:
            self._history.pop(ip, None)

        self._last_cleanup = current_time

    async def __call__(self, request: Request):
        """FastAPI Dependency check for rate limiting."""
        current_time = time.time()
        client_ip = self._get_client_ip(request)

        self._cleanup_stale_entries(current_time)

        # Filter timestamps within current sliding window
        cutoff = current_time - self.window_seconds
        timestamps = [t for t in self._history[client_ip] if t > cutoff]
        self._history[client_ip] = timestamps

        if len(timestamps) >= self.max_requests:
            retry_after = int(self.window_seconds - (current_time - timestamps[0])) + 1
            logger.warning(
                "Rate limit exceeded for IP: %s on %s (Count: %d/%d)",
                client_ip,
                request.url.path,
                len(timestamps),
                self.max_requests,
            )
            detail = self.custom_detail or f"Bạn đã gửi quá nhiều yêu cầu ({len(timestamps)}/{self.max_requests} lần). Vui lòng thử lại sau {retry_after} giây."
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=detail,
                headers={"Retry-After": str(retry_after)},
            )

        # Record this request
        self._history[client_ip].append(current_time)


# Pre-configured rate limiters
# 5 uploads per minute per IP (strict AI token cost and anti-spam protection)
upload_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
# 60 preview/get requests per minute
read_rate_limiter = SlidingWindowRateLimiter(max_requests=60, window_seconds=60)
# 10 ATS match requests per minute per IP
ats_rate_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)
# 20 STAR rewrite requests per minute per IP
star_rate_limiter = SlidingWindowRateLimiter(max_requests=20, window_seconds=60)
# 5 Harvard CV generations per day per IP (Free user tier protection)
cv_generation_rate_limiter = SlidingWindowRateLimiter(
    max_requests=5,
    window_seconds=86400,
    custom_detail="Bạn đã đạt giới hạn 5 lần tạo CV tối ưu miễn phí trong ngày. Vui lòng quay lại vào ngày mai!",
)

