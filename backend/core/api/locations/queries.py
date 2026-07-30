from core.common.database import fetch_all

LIST_CITIES_SQL = """
    SELECT DISTINCT
        VenueCity AS city
    FROM Venue
    ORDER BY VenueCity;
"""


LIST_VENUES_SQL = """
    SELECT
        VenueID AS id,
        VenueName AS name,
        VenueCity AS city,
        Capacity AS capacity
    FROM Venue
    ORDER BY
        VenueCity,
        VenueID;
"""


LIST_VENUES_BY_CITY_SQL = """
    SELECT
        VenueID AS id,
        VenueName AS name,
        VenueCity AS city,
        Capacity AS capacity
    FROM Venue
    WHERE LOWER(VenueCity) = LOWER(%s)
    ORDER BY VenueID;
"""


def get_cities() -> list[dict]:
    """
    Return all distinct cities containing at least one venue.
    """
    return fetch_all(LIST_CITIES_SQL)


def get_venues(city: str | None = None) -> list[dict]:
    """
    Return every venue.

    When city is provided, return only venues in that city.
    """
    if city is None:
        return fetch_all(LIST_VENUES_SQL)

    return fetch_all(
        LIST_VENUES_BY_CITY_SQL,
        [city],
    )
