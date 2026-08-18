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
            REDIS_URL, decode_responses=True, max_connections=100
        )
        _redis_client = redis.Redis(connection_pool=_redis_pool)
        logger.info(f"Initialized Redis connection pool to {REDIS_URL}")
    return _redis_client


async def close_redis_client():
    """Close the global async Redis client."""
    global _redis_pool, _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None
        logger.info("Closed Redis connection pool.")
