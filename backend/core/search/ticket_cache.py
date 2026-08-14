from redis.exceptions import RedisError

from core.common.redis_client import redis_client

TICKET_SEARCH_CACHE_PREFIX = "tickets:search:v2"
TICKET_SEARCH_CACHE_TTL_SECONDS = 600


def invalidate_ticket_search_cache() -> None:
    """
    Delete all cached ticket-search responses.

    Capacity changes can affect many different filter
    combinations, so the whole ticket-search namespace
    is invalidated.
    """
    try:
        keys = list(
            redis_client.scan_iter(
                match=f"{TICKET_SEARCH_CACHE_PREFIX}:*",
                count=100,
            )
        )

        if keys:
            redis_client.delete(*keys)

    except RedisError:
        # Search must continue working even when Redis
        # is temporarily unavailable.
        pass
