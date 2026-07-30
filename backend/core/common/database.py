from collections.abc import Iterable, Sequence
from contextlib import contextmanager
from typing import Any

from django.db import connection, transaction


# SQL parameters are normally passed as a list or tuple.
QueryParams = Sequence[Any] | None

# helper functions

def _get_params(params: QueryParams) -> Sequence[Any]:
    """
    Convert None into an empty parameter list.
    """
    if params is None:
        return []

    return params


def _get_column_names(cursor) -> list[str]:
    """
    Read column names from a SELECT query's result.

    """
    return [
        column[0]
        for column in cursor.description
    ]


def _row_to_dict(
    column_names: list[str],
    row: Sequence[Any],
) -> dict[str, Any]:
    """
    Convert one PostgreSQL row into a dictionary.

    Example:

        (1, "Azadi Stadium", "Tehran")

    becomes:

        {
            "id": 1,
            "name": "Azadi Stadium",
            "city": "Tehran",
        }
    """
    return dict(zip(column_names, row))



def fetch_all(
    query: str,
    params: QueryParams = None,
) -> list[dict[str, Any]]:
    """
    Execute a SELECT query and return every row as a dictionary.

    Use this when the query can return multiple records.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, _get_params(params))

        column_names = _get_column_names(cursor)
        rows = cursor.fetchall()

    return [
        _row_to_dict(column_names, row)
        for row in rows
    ]


def fetch_one(
    query: str,
    params: QueryParams = None,
) -> dict[str, Any] | None:
    """
    Execute a SELECT query and return one row as a dictionary.

    Return None when the query finds no matching row.
    
    Used when you expect zero or one row.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, _get_params(params))

        row = cursor.fetchone()

        if row is None:
            return None

        column_names = _get_column_names(cursor)

    return _row_to_dict(column_names, row)


def fetch_value(
    query: str,
    params: QueryParams = None,
) -> Any:
    """
    Execute a query and return the first value of its first row.

    Return None when the query returns no row.

    This is useful for COUNT, EXISTS, SUM, and similar queries.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, _get_params(params))

        row = cursor.fetchone()

        if row is None:
            return None

        return row[0]


def execute(
    query: str,
    params: QueryParams = None,
) -> int:
    """
    Execute an INSERT, UPDATE, or DELETE query.

    Return the number of affected rows.

    Use execute_returning() instead when you need the inserted
    or updated record back.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, _get_params(params))
        return cursor.rowcount


def execute_returning(
    query: str,
    params: QueryParams = None,
) -> dict[str, Any] | None:
    """
    Execute an INSERT, UPDATE, or DELETE query containing RETURNING.

    Return the first returned row as a dictionary.

    Return None when no row is returned.

    Example:

        reservation = execute_returning(
            '''
            INSERT INTO Reservation (
                TicketID,
                ReservationPhoneNum,
                ReservationDateTime,
                ReservationExpireDatetime,
                ReservationStatus
            )
            VALUES (
                %s,
                %s,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP + INTERVAL '10 minutes',
                'Reserved'
            )
            RETURNING
                ReservationID AS id,
                TicketID AS ticket_id,
                ReservationStatus AS status,
                ReservationExpireDatetime AS expires_at;
            ''',
            [ticket_id, phone_number],
        )
    """
    with connection.cursor() as cursor:
        cursor.execute(query, _get_params(params))

        row = cursor.fetchone()

        if row is None:
            return None

        column_names = _get_column_names(cursor)

    return _row_to_dict(column_names, row)


def execute_returning_all(
    query: str,
    params: QueryParams = None,
) -> list[dict[str, Any]]:
    """
    Execute a query containing RETURNING and return all returned rows.

    This is useful when one UPDATE or DELETE affects multiple records.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, _get_params(params))

        column_names = _get_column_names(cursor)
        rows = cursor.fetchall()

    return [
        _row_to_dict(column_names, row)
        for row in rows
    ]


def execute_many(
    query: str,
    parameter_sets: Iterable[Sequence[Any]],
) -> int:
    """
    Execute the same INSERT, UPDATE, or DELETE for multiple parameter sets.

    This is useful for bulk operations.

    Example:

        execute_many(
            '''
            INSERT INTO Venue (
                VenueCity,
                VenueName,
                Capacity
            )
            VALUES (%s, %s, %s);
            ''',
            [
                ["Tehran", "Venue One", 10000],
                ["Shiraz", "Venue Two", 12000],
            ],
        )
        
    Conceptually, this is similar to:
    
    for params in parameter_sets:
        cursor.execute(query, params)
    
    This function should not normally be needed for regular single-request
    APIs, but it is available for bulk operations.
    """
    with connection.cursor() as cursor:
        cursor.executemany(query, parameter_sets)
        return cursor.rowcount


@contextmanager
def database_transaction():
    """
    Run several database operations as one transaction.

    If every operation succeeds, Django commits the transaction.

    If any operation raises an exception, Django rolls back all operations.
    """
    with transaction.atomic():
        yield