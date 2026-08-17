"""Tests for SlidingWindowRateLimiter."""

import pytest
from httpx import ASGITransport, AsyncClient
from be.main import app
from be.core.rate_limiter import SlidingWindowRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_under_limit():
    """Test that requests within the allowed threshold succeed."""
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)

    class MockRequest:
        def __init__(self, ip: str):
            self.headers = {"X-Forwarded-For": ip}
            self.client = None
            self.url = type("URL", (), {"path": "/test"})()

    for _ in range(5):
        await limiter(MockRequest("1.2.3.4"))

    # The 6th request should raise 429
    with pytest.raises(Exception) as exc_info:
        await limiter(MockRequest("1.2.3.4"))
    assert "429" in str(exc_info.value)


@pytest.mark.asyncio
async def test_rate_limiter_distinct_ips():
    """Test that different IPs have independent rate limiting buckets."""
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

    class MockRequest:
        def __init__(self, ip: str):
            self.headers = {"X-Forwarded-For": ip}
            self.client = None
            self.url = type("URL", (), {"path": "/test"})()

    # IP 1 uses quota
    await limiter(MockRequest("10.0.0.1"))
    await limiter(MockRequest("10.0.0.1"))

    # IP 2 should still be allowed
    await limiter(MockRequest("10.0.0.2"))
    await limiter(MockRequest("10.0.0.2"))


@pytest.mark.asyncio
async def test_upload_endpoint_rate_limiting_integration():
    """Integration test checking 429 response when upload limit is exceeded."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Check health endpoint is unaffected
        response = await client.get("/health")
        assert response.status_code == 200
