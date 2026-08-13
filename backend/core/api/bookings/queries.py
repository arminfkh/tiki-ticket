import json
from typing import Any

from core.common.database import (
    fetch_all,
    fetch_one,
)


class BookingError(Exception):
    """
    An expected booking-related error.
    """

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def validate_spectator(phone_number: str) -> None:
    """
    Check that the authenticated user exists,
    is active, and is a spectator.
    """

    user = fetch_one(
        """
        SELECT
            AccountStatus AS account_status,
            UserRole AS user_role
        FROM Users
        WHERE PhoneNumber = %s;
        """,
        [phone_number],
    )

    if user is None:
        raise BookingError(
            "USER_NOT_FOUND",
            "The authenticated user does not exist.",
        )

    if user["account_status"] != "Active":
        raise BookingError(
            "USER_INACTIVE",
            "The user account is inactive.",
        )

    if user["user_role"] != "Spectator":
        raise BookingError(
            "USER_NOT_SPECTATOR",
            "Only spectator accounts can view bookings.",
        )


def get_user_bookings(
    phone_number: str,
) -> dict[str, list[dict[str, Any]]]:
    """
    Return purchased tickets for the authenticated user.

    Only reservations with a successful payment are included.
    """

    validate_spectator(phone_number)

    bookings = fetch_all(
        """
        SELECT
            r.ReservationID AS reservation_id,
            r.ReservationStatus AS reservation_status,
            r.ReservationDateTime AS reserved_at,

            t.TicketID AS ticket_id,
            t.TicketClass AS ticket_class,
            t.TicketPrice AS ticket_price,
            t.SeatNumber AS seat_number,
            t.SeatRow AS seat_row,
            t.SeatSection AS seat_section,
            t.Facilities AS facilities,

            m.MatchID AS match_id,
            m.SportType AS sport_type,
            m.HomeTeam AS home_team,
            m.AwayTeam AS away_team,
            m.MatchDatetime AS match_datetime,
            m.LeagueName AS league_name,

            v.VenueID AS venue_id,
            v.VenueName AS venue_name,
            v.VenueCity AS venue_city,

            p.PaymentAmount AS paid_amount,
            p.PaymentMethod AS payment_method,
            p.PaymentDatetime AS payment_datetime,

            CASE
                WHEN r.ReservationStatus = 'Cancelled'
                    THEN 'Cancelled'

                WHEN m.MatchDatetime <= CURRENT_TIMESTAMP
                    THEN 'Used'

                ELSE 'Upcoming'
            END AS booking_status

        FROM Reservation AS r

        JOIN Ticket AS t
            ON t.TicketID = r.TicketID

        JOIN Matches AS m
            ON m.MatchID = t.MatchID

        JOIN Venue AS v
            ON v.VenueID = m.VenueID

        JOIN Payment AS p
            ON p.ReservationID = r.ReservationID
           AND p.PaymentStatus = 'Success'

        WHERE r.ReservationPhoneNum = %s

        ORDER BY m.MatchDatetime DESC;
        """,
        [phone_number],
    )

    upcoming_tickets = []
    cancelled_tickets = []
    used_tickets = []

    for booking in bookings:
        facilities = booking.get("facilities")

        if isinstance(facilities, str):
            booking["facilities"] = json.loads(facilities)

        booking_status = booking["booking_status"]

        if booking_status == "Upcoming":
            upcoming_tickets.append(booking)

        elif booking_status == "Cancelled":
            cancelled_tickets.append(booking)

        else:
            used_tickets.append(booking)

    return {
        "upcoming_tickets": upcoming_tickets,
        "cancelled_tickets": cancelled_tickets,
        "used_tickets": used_tickets,
    }
