import logging
import os
import redis.asyncio as redis
from typing import Optional

logger = logging.getLogger(__name__)

# Default to local redis if not specified in environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis_pool: Optional[redis.ConnectionPool] = None
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get the global async Redis client instance."""
    global _redis_pool, _redis_client
    if _redis_client is None:
        _redis_pool = redis.ConnectionPool.from_url(
            REDIS_URL,
            decode_responses=True,
            max_connections=100,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
            retry_on_timeout=False,
        )
        _redis_client = redis.Redis(connection_pool=_redis_pool)
        logger.info(f"Initialized Redis connection pool to {REDIS_URL}")
    return _redis_client


async def close_redis_client():
    """Close the global async Redis client."""
    global _redis_pool, _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None
        logger.info("Closed Redis connection pool.")


async def check_redis_ready() -> bool:
    """Return whether Redis responds to a ping without exposing error details."""
    try:
        client = await get_redis_client()
        return bool(await client.ping())
    except Exception:
        logger.warning("Redis readiness check failed")
        return False
