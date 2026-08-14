from datetime import date, timedelta
from decimal import Decimal

from core.common.elasticsearch_client import elasticsearch_client

from .ticket_index import TICKET_INDEX

MAX_SEARCH_RESULTS = 10_000


SORT_OPTIONS = {
    "date_asc": [
        {"match_datetime": {"order": "asc"}},
        {"price": {"order": "asc"}},
        {"id": {"order": "asc"}},
    ],
    "date_desc": [
        {"match_datetime": {"order": "desc"}},
        {"price": {"order": "asc"}},
        {"id": {"order": "asc"}},
    ],
    "price_asc": [
        {"price": {"order": "asc"}},
        {"match_datetime": {"order": "asc"}},
        {"id": {"order": "asc"}},
    ],
    "price_desc": [
        {"price": {"order": "desc"}},
        {"match_datetime": {"order": "asc"}},
        {"id": {"order": "asc"}},
    ],
}


def _substring_filter(
    field: str,
    value: str,
) -> dict:
    """
    Build a case-insensitive substring filter.

    This mirrors the current PostgreSQL behavior:

        ILIKE '%value%'
    """
    return {
        "wildcard": {
            field: {
                "value": f"*{value}*",
                "case_insensitive": True,
            }
        }
    }


def _match_date_filter(
    match_date: date,
) -> dict:
    """
    Match every datetime occurring on one calendar date.
    """
    next_date = match_date + timedelta(days=1)

    start = f"{match_date.isoformat()}T00:00:00"
    end = f"{next_date.isoformat()}T00:00:00"

    return {
        "range": {
            "match_datetime": {
                "gte": start,
                "lt": end,
            }
        }
    }


def _deserialize_ticket(source: dict) -> dict:
    """
    Convert Elasticsearch values into a shape close to
    the existing PostgreSQL API response.
    """
    ticket = dict(source)

    if ticket.get("price") is not None:
        ticket["price"] = Decimal(str(ticket["price"])).quantize(Decimal("0.01"))

    return ticket


def search_available_tickets(
    *,
    sport: str | None = None,
    team: str | None = None,
    city: str | None = None,
    venue: str | None = None,
    ticket_class: str | None = None,
    match_date: date | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort: str = "date_asc",
) -> list[dict]:
    """
    Search available tickets using Elasticsearch.

    PostgreSQL remains the source of truth, but ticket
    discovery/search is performed against the Elasticsearch
    tickets index.
    """
    filters = [
        {
            "range": {
                "remaining_capacity": {
                    "gt": 0,
                }
            }
        },
        {
            "range": {
                "match_datetime": {
                    "gt": "now",
                }
            }
        },
    ]

    if sport is not None:
        filters.append(
            {
                "term": {
                    "sport": sport.casefold(),
                }
            }
        )

    if team is not None:
        filters.append(
            {
                "bool": {
                    "should": [
                        _substring_filter(
                            "home_team",
                            team,
                        ),
                        _substring_filter(
                            "away_team",
                            team,
                        ),
                    ],
                    "minimum_should_match": 1,
                }
            }
        )

    if city is not None:
        filters.append(
            {
                "term": {
                    "city": city.casefold(),
                }
            }
        )

    if venue is not None:
        filters.append(
            _substring_filter(
                "venue",
                venue,
            )
        )

    if ticket_class is not None:
        filters.append(
            {
                "term": {
                    "ticket_class": ticket_class.casefold(),
                }
            }
        )

    if match_date is not None:
        filters.append(
            _match_date_filter(
                match_date,
            )
        )

    if min_price is not None:
        filters.append(
            {
                "range": {
                    "price": {
                        "gte": float(min_price),
                    }
                }
            }
        )

    if max_price is not None:
        filters.append(
            {
                "range": {
                    "price": {
                        "lte": float(max_price),
                    }
                }
            }
        )

    response = elasticsearch_client.search(
        index=TICKET_INDEX,
        query={
            "bool": {
                "filter": filters,
            }
        },
        sort=SORT_OPTIONS[sort],
        size=MAX_SEARCH_RESULTS,
        track_total_hits=True,
    )

    return [_deserialize_ticket(hit["_source"]) for hit in response["hits"]["hits"]]
