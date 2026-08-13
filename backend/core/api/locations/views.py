import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from redis.exceptions import RedisError

from core.common.redis_client import redis_client
from .queries import get_cities, get_venues

CACHE_TTL_SECONDS = 600

CITIES_CACHE_KEY = "locations:cities:v1"
ALL_VENUES_CACHE_KEY = "locations:venues:v1:all"


def _read_cache(key: str):
    """
    Read and decode JSON data from Redis.

    Return None when:
    - the key does not exist;
    - Redis is unavailable;
    - the cached JSON is invalid.
    """
    try:
        cached_value = redis_client.get(key)
    except RedisError:
        return None

    if cached_value is None:
        return None

    try:
        return json.loads(cached_value)
    except json.JSONDecodeError:
        try:
            redis_client.delete(key)
        except RedisError:
            pass

        return None


def _write_cache(key: str, value) -> None:
    """
    Store a value in Redis as JSON for a limited time.
    """
    try:
        redis_client.setex(
            key,
            CACHE_TTL_SECONDS,
            json.dumps(value, ensure_ascii=False),
        )
    except RedisError:
        pass


def _get_venues_cache_key(city: str | None) -> str:
    """
    Create a separate Redis key for each city filter.
    """
    if city is None:
        return ALL_VENUES_CACHE_KEY

    normalized_city = city.casefold()

    return f"locations:venues:v1:city:{normalized_city}"


@require_GET
def list_cities(request):
    """
    Return the list of distinct cities containing venues.
    """
    cities = _read_cache(CITIES_CACHE_KEY)

    if cities is None:
        cities = get_cities()
        _write_cache(CITIES_CACHE_KEY, cities)

    return JsonResponse(
        {
            "count": len(cities),
            "cities": cities,
        }
    )


@require_GET
def list_venues(request):
    """
    Return all venues, optionally filtered by city.
    """
    city = request.GET.get("city")

    if city is not None:
        city = city.strip()

        if not city:
            return JsonResponse(
                {
                    "error": {
                        "code": "invalid_city",
                        "message": "The city parameter cannot be empty.",
                    }
                },
                status=400,
            )

    cache_key = _get_venues_cache_key(city)
    venues = _read_cache(cache_key)

    if venues is None:
        venues = get_venues(city)
        _write_cache(cache_key, venues)

    return JsonResponse(
        {
            "count": len(venues),
            "venues": venues,
        }
    )
