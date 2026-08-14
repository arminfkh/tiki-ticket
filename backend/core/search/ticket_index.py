from django.conf import settings

from core.common.elasticsearch_client import elasticsearch_client

TICKET_INDEX = settings.ELASTICSEARCH_TICKET_INDEX


TICKET_INDEX_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "normalizer": {
            "lowercase_normalizer": {
                "type": "custom",
                "filter": [
                    "lowercase",
                ],
            }
        }
    },
}


TICKET_INDEX_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "integer",
        },
        "match_id": {
            "type": "integer",
        },
        "seat_number": {
            "type": "keyword",
        },
        "seat_row": {
            "type": "keyword",
        },
        "seat_section": {
            "type": "keyword",
        },
        "ticket_class": {
            "type": "keyword",
            "normalizer": "lowercase_normalizer",
        },
        "price": {
            "type": "scaled_float",
            "scaling_factor": 100,
        },
        "remaining_capacity": {
            "type": "integer",
        },
        "sport": {
            "type": "keyword",
            "normalizer": "lowercase_normalizer",
        },
        "home_team": {
            "type": "keyword",
        },
        "away_team": {
            "type": "keyword",
        },
        "match_datetime": {
            "type": "date",
        },
        "league": {
            "type": "keyword",
        },
        "venue_id": {
            "type": "integer",
        },
        "venue": {
            "type": "keyword",
        },
        "city": {
            "type": "keyword",
            "normalizer": "lowercase_normalizer",
        },
    },
}


def ticket_index_exists() -> bool:
    """
    Return True when the Elasticsearch ticket index exists.
    """
    return elasticsearch_client.indices.exists(
        index=TICKET_INDEX,
    )


def create_ticket_index() -> None:
    """
    Create the Elasticsearch ticket index.

    Do nothing when the index already exists.
    """
    if ticket_index_exists():
        return

    elasticsearch_client.indices.create(
        index=TICKET_INDEX,
        settings=TICKET_INDEX_SETTINGS,
        mappings=TICKET_INDEX_MAPPINGS,
    )


def delete_ticket_index() -> None:
    """
    Delete the Elasticsearch ticket index when it exists.
    """
    if not ticket_index_exists():
        return

    elasticsearch_client.indices.delete(
        index=TICKET_INDEX,
    )


def recreate_ticket_index() -> None:
    """
    Delete and recreate the ticket index.
    """
    delete_ticket_index()
    create_ticket_index()
