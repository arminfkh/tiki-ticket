import json
from datetime import date
from decimal import Decimal

from core.common.database import (
    fetch_all,
    fetch_one,
)

# Used by Elasticsearch indexing/synchronization.
BASE_TICKET_SEARCH_SQL = """
    SELECT
        t.TicketID AS id,
        t.MatchID AS match_id,
        t.SeatNumber AS seat_number,
        t.SeatRow AS seat_row,
        t.SeatSection AS seat_section,
        t.TicketClass AS ticket_class,
        t.TicketPrice AS price,
        t.RemainedCapacity AS remaining_capacity,

        m.SportType AS sport,
        m.HomeTeam AS home_team,
        m.AwayTeam AS away_team,
        m.MatchDatetime AS match_datetime,
        m.LeagueName AS league,

        v.VenueID AS venue_id,
        v.VenueName AS venue,
        v.VenueCity AS city

    FROM Ticket AS t

    JOIN Matches AS m
        ON m.MatchID = t.MatchID

    JOIN Venue AS v
        ON v.VenueID = m.VenueID
"""


SORT_OPTIONS = {
    "date_asc": """
        m.MatchDatetime ASC,
        t.TicketPrice ASC,
        t.TicketID ASC
    """,
    "date_desc": """
        m.MatchDatetime DESC,
        t.TicketPrice ASC,
        t.TicketID ASC
    """,
    "price_asc": """
        t.TicketPrice ASC,
        m.MatchDatetime ASC,
        t.TicketID ASC
    """,
    "price_desc": """
        t.TicketPrice DESC,
        m.MatchDatetime ASC,
        t.TicketID ASC
    """,
}


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
    PostgreSQL implementation retained for compatibility/tests.

    The public search API currently uses Elasticsearch.
    """
    conditions = [
        "m.MatchDatetime > CURRENT_TIMESTAMP",
    ]

    params = []

    if sport is not None:
        conditions.append("LOWER(m.SportType) = LOWER(%s)")
        params.append(sport)

    if team is not None:
        conditions.append("""
            (
                m.HomeTeam ILIKE %s
                OR m.AwayTeam ILIKE %s
            )
            """)

        team_pattern = f"%{team}%"

        params.extend(
            [
                team_pattern,
                team_pattern,
            ]
        )

    if city is not None:
        conditions.append("LOWER(v.VenueCity) = LOWER(%s)")
        params.append(city)

    if venue is not None:
        conditions.append("v.VenueName ILIKE %s")
        params.append(f"%{venue}%")

    if ticket_class is not None:
        conditions.append("LOWER(t.TicketClass) = LOWER(%s)")
        params.append(ticket_class)

    if match_date is not None:
        conditions.append("m.MatchDatetime::date = %s")
        params.append(match_date)

    if min_price is not None:
        conditions.append("t.TicketPrice >= %s")
        params.append(min_price)

    if max_price is not None:
        conditions.append("t.TicketPrice <= %s")
        params.append(max_price)

    where_clause = " AND ".join(conditions)

    order_by_clause = SORT_OPTIONS[sort]

    query = f"""
        {BASE_TICKET_SEARCH_SQL}

        WHERE {where_clause}

        ORDER BY {order_by_clause};
    """

    return fetch_all(
        query,
        params,
    )


def get_ticket_availability_states(
    ticket_ids: list[int],
) -> dict[int, dict]:
    """
    Read live reservation/availability state from PostgreSQL.

    Capacity is shared across every Ticket row of one Match.
    Expired Reserved rows are treated as released immediately,
    even before another reservation endpoint physically updates
    their status/capacity.
    """
    if not ticket_ids:
        return {}

    rows = fetch_all(
        """
        SELECT
            t.TicketID AS id,

            (
                t.RemainedCapacity
                + COALESCE(
                    expired_capacity.expired_count,
                    0
                )
            ) AS remaining_capacity,

            active_reservation.status
                AS reservation_status,

            active_reservation.expires_at
                AS reservation_expires_at,

            CASE
                WHEN active_reservation.status = 'Paid'
                    THEN 'Sold'
                WHEN active_reservation.status = 'Reserved'
                    THEN 'Reserved'
                WHEN (
                    t.RemainedCapacity
                    + COALESCE(
                        expired_capacity.expired_count,
                        0
                    )
                ) <= 0
                    THEN 'Sold out'
                ELSE 'Available'
            END AS availability_status,

            (
                active_reservation.status IS NULL
                AND (
                    t.RemainedCapacity
                    + COALESCE(
                        expired_capacity.expired_count,
                        0
                    )
                ) > 0
                AND m.MatchDatetime
                    > CURRENT_TIMESTAMP
            ) AS is_selectable

        FROM Ticket AS t

        JOIN Matches AS m
            ON m.MatchID = t.MatchID

        LEFT JOIN LATERAL (
            SELECT
                COUNT(*)::INT AS expired_count
            FROM Reservation AS expired_r
            JOIN Ticket AS expired_t
                ON expired_t.TicketID
                    = expired_r.TicketID
            WHERE expired_t.MatchID
                    = t.MatchID
              AND expired_r.ReservationStatus
                    = 'Reserved'
              AND expired_r.ReservationExpireDatetime
                    <= CURRENT_TIMESTAMP
        ) AS expired_capacity
            ON TRUE

        LEFT JOIN LATERAL (
            SELECT
                r.ReservationStatus
                    AS status,
                r.ReservationExpireDatetime
                    AS expires_at
            FROM Reservation AS r
            WHERE r.TicketID
                    = t.TicketID
              AND (
                    r.ReservationStatus
                        = 'Paid'
                    OR (
                        r.ReservationStatus
                            = 'Reserved'
                        AND r.ReservationExpireDatetime
                            > CURRENT_TIMESTAMP
                    )
              )
            ORDER BY
                r.ReservationDateTime DESC,
                r.ReservationID DESC
            LIMIT 1
        ) AS active_reservation
            ON TRUE

        WHERE t.TicketID = ANY(%s);
        """,
        [ticket_ids],
    )

    return {row["id"]: row for row in rows}


GET_TICKET_DETAILS_SQL = """
    SELECT
        t.TicketID AS id,
        t.MatchID AS match_id,
        t.SeatNumber AS seat_number,
        t.SeatRow AS seat_row,
        t.SeatSection AS seat_section,
        t.TicketClass AS ticket_class,
        t.TicketPrice AS price,
        t.Facilities AS facilities,

        (
            t.RemainedCapacity
            + COALESCE(
                expired_capacity.expired_count,
                0
            )
        ) AS remaining_capacity,

        m.SportType AS sport,
        m.HomeTeam AS home_team,
        m.AwayTeam AS away_team,
        m.MatchDatetime AS match_datetime,
        m.LeagueName AS league,

        v.VenueID AS venue_id,
        v.VenueName AS venue,
        v.VenueCity AS city,
        v.Capacity AS venue_capacity,

        active_reservation.status
            AS reservation_status,

        active_reservation.expires_at
            AS reservation_expires_at,

        CASE
            WHEN active_reservation.status = 'Paid'
                THEN 'Sold'
            WHEN active_reservation.status = 'Reserved'
                THEN 'Reserved'
            WHEN (
                t.RemainedCapacity
                + COALESCE(
                    expired_capacity.expired_count,
                    0
                )
            ) <= 0
                THEN 'Sold out'
            ELSE 'Available'
        END AS availability_status,

        (
            active_reservation.status IS NULL
            AND (
                t.RemainedCapacity
                + COALESCE(
                    expired_capacity.expired_count,
                    0
                )
            ) > 0
            AND m.MatchDatetime
                > CURRENT_TIMESTAMP
        ) AS is_available,

        (
            active_reservation.status IS NULL
            AND (
                t.RemainedCapacity
                + COALESCE(
                    expired_capacity.expired_count,
                    0
                )
            ) > 0
            AND m.MatchDatetime
                > CURRENT_TIMESTAMP
        ) AS is_selectable

    FROM Ticket AS t

    JOIN Matches AS m
        ON m.MatchID = t.MatchID

    JOIN Venue AS v
        ON v.VenueID = m.VenueID

    LEFT JOIN LATERAL (
        SELECT
            COUNT(*)::INT AS expired_count
        FROM Reservation AS expired_r
        JOIN Ticket AS expired_t
            ON expired_t.TicketID
                = expired_r.TicketID
        WHERE expired_t.MatchID
                = t.MatchID
          AND expired_r.ReservationStatus
                = 'Reserved'
          AND expired_r.ReservationExpireDatetime
                <= CURRENT_TIMESTAMP
    ) AS expired_capacity
        ON TRUE

    LEFT JOIN LATERAL (
        SELECT
            r.ReservationStatus
                AS status,
            r.ReservationExpireDatetime
                AS expires_at
        FROM Reservation AS r
        WHERE r.TicketID
                = t.TicketID
          AND (
                r.ReservationStatus
                    = 'Paid'
                OR (
                    r.ReservationStatus
                        = 'Reserved'
                    AND r.ReservationExpireDatetime
                        > CURRENT_TIMESTAMP
                )
          )
        ORDER BY
            r.ReservationDateTime DESC,
            r.ReservationID DESC
        LIMIT 1
    ) AS active_reservation
        ON TRUE

    WHERE t.TicketID = %s;
"""


def get_ticket_details(
    ticket_id: int,
) -> dict | None:
    ticket = fetch_one(
        GET_TICKET_DETAILS_SQL,
        [ticket_id],
    )

    if ticket is None:
        return None

    facilities = ticket.get("facilities")

    if isinstance(
        facilities,
        str,
    ):
        try:
            ticket["facilities"] = json.loads(facilities)
        except json.JSONDecodeError:
            pass

    return ticket
