import redis

from src.core.config import settings


def initialize_redis():
    """Initialize and return a Redis client.

    The original implementation asserted that the client could successfully
    ``PING`` the configured server. During testing there might not be a running
    Redis instance which caused import time failures.  We now simply create the
    client and return it without verifying the connection so the application can
    start even if Redis is unavailable.
    """

    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


redis_client = initialize_redis()
