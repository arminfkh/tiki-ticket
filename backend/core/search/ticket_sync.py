from elasticsearch import helpers

from core.api.tickets.queries import BASE_TICKET_SEARCH_SQL
from core.common.database import fetch_all
from core.common.elasticsearch_client import elasticsearch_client

from .ticket_index import TICKET_INDEX
from .ticket_index import recreate_ticket_index

GET_ALL_TICKETS_SQL = f"""
    {BASE_TICKET_SEARCH_SQL}

    ORDER BY t.TicketID ASC;
"""


def get_all_tickets_for_indexing() -> list[dict]:
    """
    Read every ticket and its related match/venue data from PostgreSQL.

    PostgreSQL remains the source of truth.
    """
    return fetch_all(
        GET_ALL_TICKETS_SQL,
    )


def build_ticket_document(ticket: dict) -> dict:
    """
    Convert a PostgreSQL ticket row into a JSON-compatible
    Elasticsearch document.
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


def generate_ticket_bulk_actions(tickets: list[dict]):
    """
    Yield Elasticsearch bulk-index actions.

    PostgreSQL TicketID is also used as the Elasticsearch document ID.
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
    using the current PostgreSQL data.

    Return the number of indexed tickets.
    """
    tickets = get_all_tickets_for_indexing()

    recreate_ticket_index()

    if not tickets:
        return 0

    indexed_count, _ = helpers.bulk(
        elasticsearch_client,
        generate_ticket_bulk_actions(tickets),
    )

    elasticsearch_client.indices.refresh(
        index=TICKET_INDEX,
    )

    return indexed_count
