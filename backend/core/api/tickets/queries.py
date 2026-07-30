import json
from datetime import date
from decimal import Decimal

from core.common.database import fetch_all

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
        t.Facilities AS facilities,

        m.SportType AS sport,
        m.HomeTeam AS home_team,
        m.AwayTeam AS away_team,
        m.MatchDatetime AS match_datetime,
        m.LeagueName AS league,

        v.VenueID AS venue_id,
        v.VenueName AS venue,
        v.VenueCity AS city,
        v.Capacity AS venue_capacity

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
    Search available tickets using optional filters.
    """
    conditions = [
        "t.RemainedCapacity > 0",
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

    tickets = fetch_all(query, params)

    for ticket in tickets:
        facilities = ticket.get("facilities")

        if isinstance(facilities, str):
            try:
                ticket["facilities"] = json.loads(facilities)
            except json.JSONDecodeError:
                pass

    return tickets
