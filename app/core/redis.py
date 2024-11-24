from core.config import settings
import redis

def initialize_redis():
    r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    assert r.ping()
    return r


redis_client = initialize_redis()