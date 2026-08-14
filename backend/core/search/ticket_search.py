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
    next_date = match_date + timedelta(days=1)

    return {
        "range": {
            "match_datetime": {
                "gte": f"{match_date.isoformat()}T00:00:00",
                "lt": f"{next_date.isoformat()}T00:00:00",
            }
        }
    }


def _deserialize_ticket(source: dict) -> dict:
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
    Search future ticket documents in Elasticsearch.

    We intentionally do NOT remove documents whose capacity
    has reached zero here. PostgreSQL is used by the API view
    to attach the live reservation/sold/selectable state.

    This lets the frontend keep Reserved/Sold tickets visible
    while disabling selection.
    """
    filters = [
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


def get_ticket_filter_options(
    *,
    sport: str | None = None,
    city: str | None = None,
) -> dict:
    """
    Return City options and, when a city is selected,
    Venue options for future matches.

    These values come from Elasticsearch and are used by
    the searchable City/Venue dropdowns in the frontend.
    """
    filters = [
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

    aggregations = {
        "cities": {
            "terms": {
                "field": "city",
                "size": 100,
                "order": {
                    "_key": "asc",
                },
            }
        }
    }

    if city is not None:
        aggregations["venues_for_city"] = {
            "filter": {
                "term": {
                    "city": city.casefold(),
                }
            },
            "aggs": {
                "venues": {
                    "terms": {
                        "field": "venue",
                        "size": 100,
                        "order": {
                            "_key": "asc",
                        },
                    }
                }
            },
        }

    response = elasticsearch_client.search(
        index=TICKET_INDEX,
        query={
            "bool": {
                "filter": filters,
            }
        },
        aggregations=aggregations,
        size=0,
    )

    cities = [
        bucket["key"].title()
        for bucket in (response["aggregations"]["cities"]["buckets"])
    ]

    venues = []

    if city is not None:
        venues = [
            bucket["key"]
            for bucket in (
                response["aggregations"]["venues_for_city"]["venues"]["buckets"]
            )
        ]

    return {
        "cities": cities,
        "venues": venues,
    }
