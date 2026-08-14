from functools import partial

from django.db import transaction
from elasticsearch import helpers

from core.api.tickets.queries import BASE_TICKET_SEARCH_SQL
from core.common.database import fetch_all
from core.common.elasticsearch_client import elasticsearch_client

from .ticket_cache import invalidate_ticket_search_cache
from .ticket_index import TICKET_INDEX
from .ticket_index import recreate_ticket_index

GET_ALL_TICKETS_SQL = f"""
    {BASE_TICKET_SEARCH_SQL}

    ORDER BY t.TicketID ASC;
"""


GET_MATCH_TICKETS_SQL = f"""
    {BASE_TICKET_SEARCH_SQL}

    WHERE t.MatchID = %s

    ORDER BY t.TicketID ASC;
"""


def get_all_tickets_for_indexing() -> list[dict]:
    """
    Read every ticket and its related match/venue data
    from PostgreSQL.
    """
    return fetch_all(
        GET_ALL_TICKETS_SQL,
    )


def get_match_tickets_for_indexing(
    match_id: int,
) -> list[dict]:
    """
    Read every ticket belonging to one match.

    Capacity is shared between all ticket rows belonging
    to a match, so all of them must be synchronized.
    """
    return fetch_all(
        GET_MATCH_TICKETS_SQL,
        [match_id],
    )


def build_ticket_document(
    ticket: dict,
) -> dict:
    """
    Convert a PostgreSQL ticket row into an
    Elasticsearch-compatible document.
    """
    return {
        "id": ticket["id"],
        "match_id": ticket["match_id"],
        "ticket_class": ticket["ticket_class"],
        "price": float(ticket["price"]),
        "remaining_capacity": ticket["remaining_capacity"],
        "sport": ticket["sport"],
        "home_team": ticket["home_team"],
        "away_team": ticket["away_team"],
        "match_datetime": ticket["match_datetime"].isoformat(),
        "league": ticket["league"],
        "venue_id": ticket["venue_id"],
        "venue": ticket["venue"],
        "city": ticket["city"],
    }


def generate_ticket_bulk_actions(
    tickets: list[dict],
):
    """
    Yield Elasticsearch bulk indexing actions.

    PostgreSQL TicketID is also used as the
    Elasticsearch document ID.
    """
    for ticket in tickets:
        yield {
            "_index": TICKET_INDEX,
            "_id": str(ticket["id"]),
            "_source": build_ticket_document(ticket),
        }


def reindex_all_tickets() -> int:
    """
    Completely rebuild the Elasticsearch ticket index
    from PostgreSQL.
    """
    tickets = get_all_tickets_for_indexing()

    recreate_ticket_index()

    if not tickets:
        invalidate_ticket_search_cache()
        return 0

    indexed_count, _ = helpers.bulk(
        elasticsearch_client,
        generate_ticket_bulk_actions(tickets),
    )

    elasticsearch_client.indices.refresh(
        index=TICKET_INDEX,
    )

    invalidate_ticket_search_cache()

    return indexed_count


def sync_match_tickets(
    match_id: int,
) -> int:
    """
    Synchronize every Elasticsearch ticket document
    belonging to one match with PostgreSQL.

    This is used after capacity changes.
    """
    tickets = get_match_tickets_for_indexing(
        match_id,
    )

    if tickets:
        indexed_count, _ = helpers.bulk(
            elasticsearch_client,
            generate_ticket_bulk_actions(tickets),
        )

        elasticsearch_client.indices.refresh(
            index=TICKET_INDEX,
        )
    else:
        indexed_count = 0

    invalidate_ticket_search_cache()

    return indexed_count


def schedule_match_ticket_sync(
    match_id: int,
) -> None:
    """
    Synchronize Elasticsearch only after the current
    PostgreSQL transaction successfully commits.

    If PostgreSQL rolls back, the callback is discarded.
    """
    transaction.on_commit(
        partial(
            sync_match_tickets,
            match_id,
        ),
        robust=True,
    )
