import json
from typing import Any

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from core.common.database import (
    database_transaction,
    execute,
    execute_returning,
    fetch_all,
    fetch_one,
    fetch_value,
)

from core.search.ticket_sync import schedule_match_ticket_sync


class ReservationError(Exception):
    """
    An expected reservation error.
    """

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def validate_spectator(phone_number: str) -> None:
    """
    Check that the user exists, is active, and is a spectator.
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
        raise ReservationError(
            "USER_NOT_FOUND",
            "No user was found with this phone number.",
        )

    if user["account_status"] != "Active":
        raise ReservationError(
            "USER_INACTIVE",
            "The user account is inactive.",
        )

    if user["user_role"] != "Spectator":
        raise ReservationError(
            "USER_NOT_SPECTATOR",
            "Only spectator accounts can reserve tickets.",
        )


def prepare_match_capacity(
    match_id: int,
    phone_number: str | None = None,
) -> tuple[int, int]:
    """
    Lock every ticket belonging to the match.

    Cancel expired reservations and restore their capacity.

    If phone_number is given, only that user's expired
    reservations are cancelled.

    Return:
        ticket_count
        current_remaining_capacity
    """

    match_tickets = fetch_all(
        """
        SELECT
            TicketID AS ticket_id,
            RemainedCapacity AS remained_capacity
        FROM Ticket
        WHERE MatchID = %s
        ORDER BY TicketID
        FOR UPDATE;
        """,
        [match_id],
    )

    if not match_tickets:
        raise RuntimeError("No tickets were found for this match.")

    capacities = {ticket["remained_capacity"] for ticket in match_tickets}

    if len(capacities) != 1:
        raise RuntimeError(
            "The remaining capacities for this match " "are not synchronized."
        )

    current_capacity = next(iter(capacities))

    if phone_number is None:
        expired_count = fetch_value(
            """
            WITH expired AS (
                UPDATE Reservation AS r
                SET ReservationStatus = 'Cancelled'
                FROM Ticket AS t
                WHERE r.TicketID = t.TicketID
                  AND t.MatchID = %s
                  AND r.ReservationStatus = 'Reserved'
                  AND r.ReservationExpireDatetime
                      <= CURRENT_TIMESTAMP
                RETURNING r.ReservationID
            )
            SELECT COUNT(*)
            FROM expired;
            """,
            [match_id],
        )
    else:
        expired_count = fetch_value(
            """
            WITH expired AS (
                UPDATE Reservation AS r
                SET ReservationStatus = 'Cancelled'
                FROM Ticket AS t
                WHERE r.TicketID = t.TicketID
                  AND t.MatchID = %s
                  AND r.ReservationPhoneNum = %s
                  AND r.ReservationStatus = 'Reserved'
                  AND r.ReservationExpireDatetime
                      <= CURRENT_TIMESTAMP
                RETURNING r.ReservationID
            )
            SELECT COUNT(*)
            FROM expired;
            """,
            [match_id, phone_number],
        )

    expired_count = int(expired_count or 0)

    if expired_count > 0:
        updated_count = execute(
            """
            UPDATE Ticket
            SET RemainedCapacity =
                RemainedCapacity + %s
            WHERE MatchID = %s;
            """,
            [expired_count, match_id],
        )

        if updated_count != len(match_tickets):
            raise RuntimeError("Not all ticket capacities were restored.")

        current_capacity += expired_count

    return len(match_tickets), current_capacity


# Reserve a ticket


def create_reservation(
    ticket_id: int,
    phone_number: str,
) -> dict[str, Any]:
    """
    Reserve one specific ticket for ten minutes.
    """

    with database_transaction():
        validate_spectator(phone_number)

        ticket = fetch_one(
            """
            SELECT
                t.TicketID AS ticket_id,
                t.MatchID AS match_id,
                m.MatchDatetime AS match_datetime,
                (
                    m.MatchDatetime <= CURRENT_TIMESTAMP
                ) AS match_started
            FROM Ticket AS t
            JOIN Matches AS m
                ON m.MatchID = t.MatchID
            WHERE t.TicketID = %s;
            """,
            [ticket_id],
        )

        if ticket is None:
            raise ReservationError(
                "TICKET_NOT_FOUND",
                "The requested ticket does not exist.",
            )

        if ticket["match_started"]:
            raise ReservationError(
                "MATCH_STARTED",
                "Tickets cannot be reserved after the match has started.",
            )

        match_id = ticket["match_id"]

        ticket_count, remaining_capacity = prepare_match_capacity(match_id)

        # Check whether this specific ticket is already reserved or sold.
        existing_reservation = fetch_one(
            """
            SELECT
                ReservationPhoneNum AS phone_number,
                ReservationStatus AS status
            FROM Reservation
            WHERE TicketID = %s
              AND ReservationStatus IN ('Reserved', 'Paid')
            ORDER BY ReservationDateTime DESC
            LIMIT 1;
            """,
            [ticket_id],
        )

        if existing_reservation is not None:
            if existing_reservation["status"] == "Paid":
                raise ReservationError(
                    "TICKET_ALREADY_SOLD",
                    "This ticket has already been purchased.",
                )

            if existing_reservation["phone_number"] == phone_number:
                raise ReservationError(
                    "ACTIVE_RESERVATION_EXISTS",
                    ("You already have an active " "reservation for this ticket."),
                )

            raise ReservationError(
                "TICKET_ALREADY_RESERVED",
                ("This ticket is currently reserved " "by another user."),
            )

        if remaining_capacity <= 0:
            raise ReservationError(
                "TICKET_SOLD_OUT",
                "No remaining capacity is available for this match.",
            )

        # Capacity is shared by all tickets belonging to the match.
        updated_count = execute(
            """
            UPDATE Ticket
            SET RemainedCapacity =
                RemainedCapacity - 1
            WHERE MatchID = %s;
            """,
            [match_id],
        )

        if updated_count != ticket_count:
            raise RuntimeError("Not all ticket capacities were decreased.")

        reservation = execute_returning(
            """
            INSERT INTO Reservation (
                TicketID,
                ReservationPhoneNum,
                CancellationPhoneNum,
                ReservationDateTime,
                ReservationExpireDatetime,
                ReservationStatus
            )
            VALUES (
                %s,
                %s,
                NULL,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
                    + INTERVAL '10 minutes',
                'Reserved'
            )
            RETURNING
                ReservationID AS reservation_id,
                TicketID AS ticket_id,
                ReservationPhoneNum AS phone_number,
                ReservationDateTime AS reserved_at,
                ReservationExpireDatetime AS expires_at,
                ReservationStatus AS status;
            """,
            [ticket_id, phone_number],
        )

        if reservation is None:
            raise RuntimeError("The reservation was not returned by PostgreSQL.")

        reservation["match_id"] = match_id
        reservation["remained_capacity"] = remaining_capacity - 1

        schedule_match_ticket_sync(match_id)

        return reservation


def get_user_reservations(
    phone_number: str,
) -> dict[str, list[dict[str, Any]]]:
    """
    Return active reservations and reservation history.
    """

    with database_transaction():
        validate_spectator(phone_number)

        # Find matches where this user has expired reservations.
        expired_matches = fetch_all(
            """
            SELECT DISTINCT
                t.MatchID AS match_id
            FROM Reservation AS r
            JOIN Ticket AS t
                ON t.TicketID = r.TicketID
            WHERE r.ReservationPhoneNum = %s
              AND r.ReservationStatus = 'Reserved'
              AND r.ReservationExpireDatetime
                  <= CURRENT_TIMESTAMP
            ORDER BY t.MatchID;
            """,
            [phone_number],
        )

        # Cancel expired reservations and restore match capacity.
        for match in expired_matches:
            prepare_match_capacity(
                match_id=match["match_id"],
                phone_number=phone_number,
            )

            schedule_match_ticket_sync(match["match_id"])

        reservations = fetch_all(
            """
            SELECT
                r.ReservationID AS reservation_id,
                r.ReservationStatus AS status,
                r.ReservationDateTime AS reserved_at,
                r.ReservationExpireDatetime AS expires_at,

                t.TicketID AS ticket_id,
                t.TicketClass AS ticket_class,
                t.TicketPrice AS ticket_price,
                t.SeatNumber AS seat_number,
                t.SeatRow AS seat_row,
                t.SeatSection AS seat_section,
                t.Facilities AS facilities,
                t.RemainedCapacity AS remained_capacity,

                m.MatchID AS match_id,
                m.SportType AS sport_type,
                m.HomeTeam AS home_team,
                m.AwayTeam AS away_team,
                m.MatchDatetime AS match_datetime,
                m.LeagueName AS league_name,

                v.VenueID AS venue_id,
                v.VenueName AS venue_name,
                v.VenueCity AS venue_city,

                CASE
                    WHEN r.ReservationStatus = 'Reserved'
                    THEN GREATEST(
                        EXTRACT(
                            EPOCH FROM (
                                r.ReservationExpireDatetime
                                - CURRENT_TIMESTAMP
                            )
                        )::INT,
                        0
                    )
                    ELSE NULL
                END AS remaining_seconds

            FROM Reservation AS r
            JOIN Ticket AS t
                ON t.TicketID = r.TicketID
            JOIN Matches AS m
                ON m.MatchID = t.MatchID
            JOIN Venue AS v
                ON v.VenueID = m.VenueID

            WHERE r.ReservationPhoneNum = %s

            ORDER BY r.ReservationDateTime DESC;
            """,
            [phone_number],
        )

    active_reservations = []
    reservation_history = []

    for reservation in reservations:
        facilities = reservation.get("facilities")

        if isinstance(facilities, str):
            reservation["facilities"] = json.loads(facilities)

        if reservation["status"] == "Reserved":
            active_reservations.append(reservation)
        else:
            reservation.pop(
                "remaining_seconds",
                None,
            )
            reservation_history.append(reservation)

    return {
        "active_reservations": active_reservations,
        "reservation_history": reservation_history,
    }


# Calculate cancelation penalty


def calculate_cancellation_penalty(
    match_datetime: datetime,
    paid_amount: Decimal,
) -> dict[str, Any]:
    """
    Calculate a cancellation quote based on the remaining
    time before the match.

    This function does not read from or modify the database.
    """

    # MatchDatetime may be timezone-aware or timezone-naive,
    # depending on the PostgreSQL/Django configuration.
    if match_datetime.tzinfo is None:
        current_time = datetime.now()
    else:
        current_time = datetime.now(tz=match_datetime.tzinfo)

    seconds_until_match = (match_datetime - current_time).total_seconds()

    paid_amount = Decimal(str(paid_amount))

    # The match has already started.
    if seconds_until_match <= 0:
        return {
            "can_cancel": False,
            "hours_until_match": 0,
            "penalty_percentage": Decimal("100.00"),
            "penalty_amount": paid_amount,
            "refund_amount": Decimal("0.000"),
            "reason": "The match has already started.",
        }

    hours_until_match = (Decimal(str(seconds_until_match)) / Decimal("3600")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    if seconds_until_match >= 7 * 24 * 60 * 60:
        penalty_percentage = Decimal("10.00")
    elif seconds_until_match >= 3 * 24 * 60 * 60:
        penalty_percentage = Decimal("20.00")
    elif seconds_until_match >= 24 * 60 * 60:
        penalty_percentage = Decimal("40.00")
    else:
        penalty_percentage = Decimal("70.00")

    penalty_amount = (paid_amount * penalty_percentage / Decimal("100")).quantize(
        Decimal("0.001"),
        rounding=ROUND_HALF_UP,
    )

    refund_amount = (paid_amount - penalty_amount).quantize(
        Decimal("0.001"),
        rounding=ROUND_HALF_UP,
    )

    return {
        "can_cancel": True,
        "hours_until_match": hours_until_match,
        "penalty_percentage": penalty_percentage,
        "penalty_amount": penalty_amount,
        "refund_amount": refund_amount,
        "reason": (
            "The penalty is calculated from the time " "remaining before the match."
        ),
    }


def get_cancellation_quote(
    reservation_id: int,
    phone_number: str,
) -> dict[str, Any]:
    """
    Return a cancellation quote for a paid reservation.

    This function does not cancel the reservation and does
    not modify any database records.
    """

    validate_spectator(phone_number)

    reservation = fetch_one(
        """
        SELECT
            r.ReservationID AS reservation_id,
            r.ReservationPhoneNum AS phone_number,
            r.ReservationStatus AS reservation_status,

            t.TicketID AS ticket_id,
            t.TicketClass AS ticket_class,

            m.MatchID AS match_id,
            m.HomeTeam AS home_team,
            m.AwayTeam AS away_team,
            m.MatchDatetime AS match_datetime,

            (
                SELECT p.PaymentAmount
                FROM Payment AS p
                WHERE p.ReservationID = r.ReservationID
                  AND p.PaymentStatus = 'Success'
                ORDER BY
                    p.PaymentDatetime DESC,
                    p.PaymentID DESC
                LIMIT 1
            ) AS paid_amount

        FROM Reservation AS r
        JOIN Ticket AS t
            ON t.TicketID = r.TicketID
        JOIN Matches AS m
            ON m.MatchID = t.MatchID

        WHERE r.ReservationID = %s;
        """,
        [reservation_id],
    )

    if reservation is None:
        raise ReservationError(
            "RESERVATION_NOT_FOUND",
            "The requested reservation does not exist.",
        )

    if reservation["phone_number"] != phone_number:
        raise ReservationError(
            "RESERVATION_NOT_OWNED",
            "This reservation belongs to another user.",
        )

    if reservation["reservation_status"] != "Paid":
        raise ReservationError(
            "RESERVATION_NOT_PAID",
            ("Only paid reservations can receive " "a cancellation quote."),
        )

    if reservation["paid_amount"] is None:
        raise ReservationError(
            "SUCCESSFUL_PAYMENT_NOT_FOUND",
            ("No successful payment was found " "for this reservation."),
        )

    penalty = calculate_cancellation_penalty(
        match_datetime=reservation["match_datetime"],
        paid_amount=reservation["paid_amount"],
    )

    return {
        "reservation_id": reservation["reservation_id"],
        "ticket_id": reservation["ticket_id"],
        "ticket_class": reservation["ticket_class"],
        "match_id": reservation["match_id"],
        "home_team": reservation["home_team"],
        "away_team": reservation["away_team"],
        "match_datetime": reservation["match_datetime"],
        "paid_amount": reservation["paid_amount"],
        **penalty,
    }


# Cancle a reservation


def cancel_paid_reservation(
    reservation_id: int,
    phone_number: str,
) -> dict[str, Any]:
    """
    Cancel a paid reservation and refund the allowed amount
    to the authenticated user's wallet.
    """

    with database_transaction():
        validate_spectator(phone_number)

        reservation = fetch_one(
            """
            SELECT
                r.ReservationID AS reservation_id,
                r.ReservationPhoneNum AS phone_number,
                r.ReservationStatus AS reservation_status,

                t.TicketID AS ticket_id,
                t.TicketClass AS ticket_class,

                m.MatchID AS match_id,
                m.HomeTeam AS home_team,
                m.AwayTeam AS away_team,
                m.MatchDatetime AS match_datetime,

                (
                    SELECT p.PaymentAmount
                    FROM Payment AS p
                    WHERE p.ReservationID = r.ReservationID
                      AND p.PaymentStatus = 'Success'
                    ORDER BY
                        p.PaymentDatetime DESC,
                        p.PaymentID DESC
                    LIMIT 1
                ) AS paid_amount

            FROM Reservation AS r
            JOIN Ticket AS t
                ON t.TicketID = r.TicketID
            JOIN Matches AS m
                ON m.MatchID = t.MatchID

            WHERE r.ReservationID = %s

            FOR UPDATE OF r;
            """,
            [reservation_id],
        )

        if reservation is None:
            raise ReservationError(
                "RESERVATION_NOT_FOUND",
                "The requested reservation does not exist.",
            )

        if reservation["phone_number"] != phone_number:
            raise ReservationError(
                "RESERVATION_NOT_OWNED",
                "This reservation belongs to another user.",
            )

        if reservation["reservation_status"] == "Cancelled":
            raise ReservationError(
                "RESERVATION_ALREADY_CANCELLED",
                "This reservation has already been cancelled.",
            )

        if reservation["reservation_status"] != "Paid":
            raise ReservationError(
                "RESERVATION_NOT_PAID",
                "Only paid reservations can be cancelled.",
            )

        if reservation["paid_amount"] is None:
            raise ReservationError(
                "SUCCESSFUL_PAYMENT_NOT_FOUND",
                "No successful payment was found for this reservation.",
            )

        penalty = calculate_cancellation_penalty(
            match_datetime=reservation["match_datetime"],
            paid_amount=reservation["paid_amount"],
        )

        if not penalty["can_cancel"]:
            raise ReservationError(
                "MATCH_STARTED",
                "The ticket cannot be cancelled after the match has started.",
            )

        match_id = reservation["match_id"]

        # Lock match tickets and make sure shared capacity is synchronized.
        ticket_count, current_capacity = prepare_match_capacity(match_id)

        cancelled_reservation = execute_returning(
            """
            UPDATE Reservation
            SET
                ReservationStatus = 'Cancelled',
                CancellationPhoneNum = %s
            WHERE ReservationID = %s
              AND ReservationStatus = 'Paid'
            RETURNING
                ReservationID AS reservation_id,
                TicketID AS ticket_id,
                ReservationPhoneNum AS phone_number,
                CancellationPhoneNum AS cancellation_phone_number,
                ReservationStatus AS status;
            """,
            [
                phone_number,
                reservation_id,
            ],
        )

        if cancelled_reservation is None:
            raise RuntimeError("The reservation could not be cancelled.")

        # Return one seat to the shared match capacity.
        updated_count = execute(
            """
            UPDATE Ticket
            SET RemainedCapacity = RemainedCapacity + 1
            WHERE MatchID = %s;
            """,
            [match_id],
        )

        if updated_count != ticket_count:
            raise RuntimeError("Not all ticket capacities were restored.")

        wallet = execute_returning(
            """
            UPDATE Users
            SET WalletBalance = WalletBalance + %s
            WHERE PhoneNumber = %s
            RETURNING
                WalletBalance AS wallet_balance;
            """,
            [
                penalty["refund_amount"],
                phone_number,
            ],
        )

        if wallet is None:
            raise RuntimeError("The refund could not be added to the user's wallet.")

        schedule_match_ticket_sync(match_id)

        return {
            "reservation": cancelled_reservation,
            "match": {
                "match_id": reservation["match_id"],
                "home_team": reservation["home_team"],
                "away_team": reservation["away_team"],
                "match_datetime": reservation["match_datetime"],
            },
            "refund": {
                "paid_amount": reservation["paid_amount"],
                "penalty_percentage": penalty["penalty_percentage"],
                "penalty_amount": penalty["penalty_amount"],
                "refund_amount": penalty["refund_amount"],
            },
            "wallet_balance": wallet["wallet_balance"],
            "remained_capacity": current_capacity + 1,
        }
