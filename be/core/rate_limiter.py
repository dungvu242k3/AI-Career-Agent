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

    MAX_IN_MEMORY_IPS = 10000

    def _cleanup_stale_entries(self, current_time: float):
        """Periodically purge expired timestamps and enforce memory bounds."""
        if current_time - self._last_cleanup < 60 and len(self._history) < self.MAX_IN_MEMORY_IPS:
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

        # If memory is still full after pruning, evict the oldest 20% of entries
        if len(self._history) >= self.MAX_IN_MEMORY_IPS:
            excess = len(self._history) - int(self.MAX_IN_MEMORY_IPS * 0.8)
            for ip in list(self._history.keys())[:excess]:
                self._history.pop(ip, None)

        self._last_cleanup = current_time


    async def __call__(self, request: Request):
        """FastAPI Dependency check for rate limiting."""
        current_time = time.time()
        client_ip = self._get_client_ip(request)

        self._cleanup_stale_entries(current_time)
        cutoff = current_time - self.window_seconds

        # 1. Try Redis for distributed Rate Limiting
        try:
            from be.core.redis_client import get_redis_client
            redis_client = await get_redis_client()
            if redis_client:
                key = f"rate_limit:{request.url.path}:{client_ip}"
                async with redis_client.pipeline(transaction=True) as pipe:
                    pipe.zremrangebyscore(key, 0, cutoff)
                    pipe.zadd(key, {str(current_time): current_time})
                    pipe.zcard(key)
                    pipe.expire(key, self.window_seconds)
                    results = await pipe.execute()
                
                request_count = results[2]
                
                if request_count > self.max_requests:
                    oldest_res = await redis_client.zrange(key, 0, 0, withscores=True)
                    if oldest_res:
                        oldest_ts = oldest_res[0][1]
                        retry_after = int(self.window_seconds - (current_time - oldest_ts)) + 1
                    else:
                        retry_after = self.window_seconds
                        
                    logger.warning(
                        "Rate limit exceeded (Redis) for IP: %s on %s (Count: %d/%d)",
                        client_ip,
                        request.url.path,
                        request_count,
                        self.max_requests,
                    )
                    detail = self.custom_detail or f"Bạn đã gửi quá nhiều yêu cầu ({request_count}/{self.max_requests} lần). Vui lòng thử lại sau {retry_after} giây."
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=detail,
                        headers={"Retry-After": str(retry_after)},
                    )
                return
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("Redis rate limiting failed: %s. Falling back to in-memory.", e)

        # 2. Fallback to in-memory Rate Limiting
        timestamps = [t for t in self._history[client_ip] if t > cutoff]
        self._history[client_ip] = timestamps

        if len(timestamps) >= self.max_requests:
            retry_after = int(self.window_seconds - (current_time - timestamps[0])) + 1
            logger.warning(
                "Rate limit exceeded (Memory) for IP: %s on %s (Count: %d/%d)",
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
# 20 Chat requests per minute
chat_rate_limiter = SlidingWindowRateLimiter(max_requests=20, window_seconds=60)
# 5 Mock Interview starts per minute
interview_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)


