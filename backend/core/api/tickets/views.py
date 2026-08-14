import hashlib
import json
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from redis.exceptions import RedisError

from core.common.redis_client import redis_client

from core.search.ticket_search import (
    get_ticket_filter_options,
    search_available_tickets,
)

from .queries import get_ticket_details

from elasticsearch import ApiError, TransportError

from core.search.ticket_cache import (
    TICKET_SEARCH_CACHE_PREFIX,
    TICKET_SEARCH_CACHE_TTL_SECONDS,
)

ALLOWED_SPORTS = {
    "football",
    "volleyball",
    "basketball",
}

ALLOWED_TICKET_CLASSES = {
    "regular",
    "premium",
    "vip",
}

ALLOWED_SORT_OPTIONS = {
    "date_asc",
    "date_desc",
    "price_asc",
    "price_desc",
}


def _error_response(
    code: str,
    message: str,
) -> JsonResponse:
    return JsonResponse(
        {
            "error": {
                "code": code,
                "message": message,
            }
        },
        status=400,
    )


def _get_text_parameter(
    request,
    name: str,
) -> str | None:
    """
    Read and clean an optional text query parameter.

    Raise ValueError if the parameter exists but is empty.
    """
    value = request.GET.get(name)

    if value is None:
        return None

    value = value.strip()

    if not value:
        raise ValueError(f"The {name} parameter cannot be empty.")

    return value


def _get_price_parameter(
    request,
    name: str,
) -> Decimal | None:
    """
    Read and validate an optional non-negative price.
    """
    value = request.GET.get(name)

    if value is None:
        return None

    value = value.strip()

    if not value:
        raise ValueError(f"The {name} parameter cannot be empty.")

    try:
        price = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"The {name} parameter must be a valid number.") from exc

    if not price.is_finite() or price < 0:
        raise ValueError(f"The {name} parameter must be a non-negative number.")

    return price


def _get_date_parameter(request) -> date | None:
    """
    Read an optional date in YYYY-MM-DD format.
    """
    value = request.GET.get("date")

    if value is None:
        return None

    value = value.strip()

    if not value:
        raise ValueError("The date parameter cannot be empty.")

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("The date parameter must use YYYY-MM-DD format.") from exc


def _read_cache(key: str):
    """
    Read JSON data from Redis.

    Return None when:
    - the cache entry does not exist;
    - Redis is unavailable;
    - the cached value contains invalid JSON.
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
    Store a JSON-compatible value in Redis temporarily.
    """
    try:
        serialized_value = json.dumps(
            value,
            cls=DjangoJSONEncoder,
            ensure_ascii=False,
        )

        redis_client.setex(
            key,
            TICKET_SEARCH_CACHE_TTL_SECONDS,
            serialized_value,
        )
    except RedisError:
        pass


def _normalize_decimal_for_cache(
    value: Decimal | None,
) -> str | None:
    """
    Convert equivalent Decimal values into the same cache value.

    For example:
        Decimal("50.0")
        Decimal("50.00")

    both become:
        "50"
    """
    if value is None:
        return None

    return format(value.normalize(), "f")


# functions for building a unique hash key
def _normalize_text_for_cache(
    value: str | None,
) -> str | None:
    """
    Normalize case-insensitive text filters.
    """
    if value is None:
        return None

    return value.casefold()


def _build_ticket_search_cache_key(
    *,
    sport: str | None,
    team: str | None,
    city: str | None,
    venue: str | None,
    ticket_class: str | None,
    match_date: date | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    sort: str,
) -> str:
    """
    Build a stable cache key for one filter combination.
    """
    filter_data = {
        "sport": _normalize_text_for_cache(sport),
        "team": _normalize_text_for_cache(team),
        "city": _normalize_text_for_cache(city),
        "venue": _normalize_text_for_cache(venue),
        "ticket_class": _normalize_text_for_cache(ticket_class),
        "date": (match_date.isoformat() if match_date is not None else None),
        "min_price": _normalize_decimal_for_cache(min_price),
        "max_price": _normalize_decimal_for_cache(max_price),
        "sort": sort,
    }

    serialized_filters = json.dumps(
        filter_data,
        sort_keys=True,
        separators=(",", ":"),
    )

    filter_hash = hashlib.sha256(serialized_filters.encode("utf-8")).hexdigest()

    return f"{TICKET_SEARCH_CACHE_PREFIX}:" f"{filter_hash}"


@require_GET
def search_tickets(request):
    """
    Search available tickets using optional query parameters.
    """
    try:
        sport = _get_text_parameter(request, "sport")
        team = _get_text_parameter(request, "team")
        city = _get_text_parameter(request, "city")
        venue = _get_text_parameter(request, "venue")
        ticket_class = _get_text_parameter(
            request,
            "ticket_class",
        )

        match_date = _get_date_parameter(request)

        min_price = _get_price_parameter(
            request,
            "min_price",
        )
        max_price = _get_price_parameter(
            request,
            "max_price",
        )

        sort = _get_text_parameter(request, "sort") or "date_asc"

    except ValueError as exc:
        return _error_response(
            "invalid_parameter",
            str(exc),
        )

    if sport is not None and sport.casefold() not in ALLOWED_SPORTS:
        return _error_response(
            "invalid_sport",
            ("Sport must be Football, Volleyball, " "or Basketball."),
        )

    if (
        ticket_class is not None
        and ticket_class.casefold() not in ALLOWED_TICKET_CLASSES
    ):
        return _error_response(
            "invalid_ticket_class",
            ("Ticket class must be Regular, Premium, " "or VIP."),
        )

    if sort not in ALLOWED_SORT_OPTIONS:
        return _error_response(
            "invalid_sort",
            ("Sort must be date_asc, date_desc, " "price_asc, or price_desc."),
        )

    if min_price is not None and max_price is not None and min_price > max_price:
        return _error_response(
            "invalid_price_range",
            ("The min_price parameter cannot be greater " "than max_price."),
        )

    cache_key = _build_ticket_search_cache_key(
        sport=sport,
        team=team,
        city=city,
        venue=venue,
        ticket_class=ticket_class,
        match_date=match_date,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )

    tickets = _read_cache(cache_key)

    if tickets is None:
        try:
            tickets = search_available_tickets(
                sport=sport,
                team=team,
                city=city,
                venue=venue,
                ticket_class=ticket_class,
                match_date=match_date,
                min_price=min_price,
                max_price=max_price,
                sort=sort,
            )
        except (ApiError, TransportError):
            return JsonResponse(
                {
                    "error": {
                        "code": "search_service_unavailable",
                        "message": (
                            "The ticket search service is temporarily unavailable."
                        ),
                    }
                },
                status=503,
            )

        _write_cache(cache_key, tickets)

    return JsonResponse(
        {
            "count": len(tickets),
            "tickets": tickets,
        }
    )


@require_GET
def ticket_filter_options(request):
    """
    Return dynamic city and venue options for ticket filters.
    """
    try:
        sport = _get_text_parameter(request, "sport")
        city = _get_text_parameter(request, "city")

    except ValueError as exc:
        return _error_response(
            "invalid_parameter",
            str(exc),
        )

    if sport is not None and sport.casefold() not in ALLOWED_SPORTS:
        return _error_response(
            "invalid_sport",
            ("Sport must be Football, Volleyball, " "or Basketball."),
        )

    try:
        options = get_ticket_filter_options(
            sport=sport,
            city=city,
        )

    except (ApiError, TransportError):
        return JsonResponse(
            {
                "error": {
                    "code": "search_service_unavailable",
                    "message": (
                        "The ticket search service is temporarily unavailable."
                    ),
                }
            },
            status=503,
        )

    return JsonResponse(options)


# api 6
@require_GET
def ticket_details(request, ticket_id: int):
    """
    Return complete information for one ticket.
    """
    ticket = get_ticket_details(ticket_id)

    if ticket is None:
        return JsonResponse(
            {
                "error": {
                    "code": "ticket_not_found",
                    "message": "No ticket was found with this ID.",
                }
            },
            status=404,
        )

    return JsonResponse(
        {
            "ticket": ticket,
        }
    )
