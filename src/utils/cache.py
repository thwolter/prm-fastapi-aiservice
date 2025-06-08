import logging

from src.core.config import settings
from src.core.redis import initialize_redis

logger = logging.getLogger(__name__)


def redis_cache(timeout: int = settings.CACHE_TIMEOUT, redis_client=None):
    """
    Decorator for caching results in Redis with default timeout and client.

    :param redis_client: Redis client instance (default: initializes a new client).
    :param timeout: Cache expiration time in seconds (default: 300 seconds).
    """
    if redis_client is None:
        redis_client = initialize_redis()

    def decorator(func):
        async def wrapper(self, query, *args, **kwargs):
            # Generate a cache key based on the query and service parameters
            # the class must define a `generate_cache_key` method
            cache_key = self.generate_cache_key(query, *args, **kwargs)
            cached_result = redis_client.get(cache_key)
            if cached_result:
                logger.debug(f'Cache hit for key: {cache_key}')
                return self.ResultModel.parse_raw(cached_result)

            result = await func(self, query, *args, **kwargs)
            redis_client.set(cache_key, result.json(), ex=timeout)
            logger.debug(f'Cache miss, key stored: {cache_key}')
            return result

        return wrapper

    return decorator
