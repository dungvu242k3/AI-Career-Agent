"""High-performance Sliding Window Rate Limiter for FastAPI.

Protects expensive AI endpoints (CV parsing, LLM generation) from DoS, brute-force,
and token quota exhaustion attacks.
"""

from collections import defaultdict
import logging
import time
from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter tracking client IP requests."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Storage: ip -> list of unix timestamps
        self._history: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup: float = time.time()

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP handling reverse proxy headers (X-Forwarded-For)."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # First IP in comma-separated list is client IP
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "127.0.0.1"

    def _cleanup_stale_entries(self, current_time: float):
        """Periodically purge expired timestamps to prevent memory growth."""
        if current_time - self._last_cleanup < 300:  # Cleanup every 5 minutes
            return

        cutoff = current_time - self.window_seconds
        stale_ips = []
        for ip, timestamps in self._history.items():
            self._history[ip] = [t for t in timestamps if t > cutoff]
            if not self._history[ip]:
                stale_ips.append(ip)

        for ip in stale_ips:
            del self._history[ip]

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
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Bạn đã gửi quá nhiều yêu cầu ({len(timestamps)}/{self.max_requests} lần/phút). Vui lòng thử lại sau {retry_after} giây.",
                headers={"Retry-After": str(retry_after)},
            )

        # Record this request
        self._history[client_ip].append(current_time)


# Pre-configured rate limiters
# 5 uploads per minute per IP (strict AI token cost and anti-spam protection)
upload_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
# 60 preview/get requests per minute
read_rate_limiter = SlidingWindowRateLimiter(max_requests=60, window_seconds=60)
