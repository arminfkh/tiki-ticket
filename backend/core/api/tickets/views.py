from datetime import date
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .queries import search_available_tickets

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

    return JsonResponse(
        {
            "count": len(tickets),
            "tickets": tickets,
        }
    )
