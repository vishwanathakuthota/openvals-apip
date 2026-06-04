from redis import Redis

from app.core.config import settings


def redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
