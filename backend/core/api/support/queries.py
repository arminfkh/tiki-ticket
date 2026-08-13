from typing import Any

from core.common.database import (
    database_transaction,
    execute,
    execute_returning,
    fetch_all,
    fetch_one,
)

from core.api.reservations.queries import (
    calculate_cancellation_penalty,
)


class SupportError(Exception):
    """
    An expected support-related error.
    """

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def validate_support(phone_number: str) -> None:
    """
    Check that the authenticated user exists,
    is active, and has the Support role.
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
        raise SupportError(
            "USER_NOT_FOUND",
            "The authenticated user does not exist.",
        )

    if user["account_status"] != "Active":
        raise SupportError(
            "USER_INACTIVE",
            "The support account is inactive.",
        )

    if user["user_role"] != "Support":
        raise SupportError(
            "USER_NOT_SUPPORT",
            "Only support accounts can access this API.",
        )


def get_support_overview(
    support_phone_number: str,
) -> dict[str, Any]:
    """
    Return information required by the support dashboard.
    """

    validate_support(support_phone_number)

    cancelled_tickets = fetch_all("""
        SELECT
            r.ReservationID AS reservation_id,
            r.ReservationPhoneNum AS user_phone_number,
            r.CancellationPhoneNum AS cancellation_phone_number,
            r.ReservationDateTime AS reserved_at,
            r.ReservationStatus AS status,

            t.TicketID AS ticket_id,
            t.TicketClass AS ticket_class,
            t.TicketPrice AS ticket_price,
            t.SeatNumber AS seat_number,
            t.SeatRow AS seat_row,
            t.SeatSection AS seat_section,

            m.MatchID AS match_id,
            m.HomeTeam AS home_team,
            m.AwayTeam AS away_team,
            m.MatchDatetime AS match_datetime,

            v.VenueName AS venue_name,
            v.VenueCity AS venue_city

        FROM Reservation AS r

        JOIN Ticket AS t
            ON t.TicketID = r.TicketID

        JOIN Matches AS m
            ON m.MatchID = t.MatchID

        JOIN Venue AS v
            ON v.VenueID = m.VenueID

        WHERE r.ReservationStatus = 'Cancelled'

        ORDER BY r.ReservationDateTime DESC;
        """)

    manageable_reservations = fetch_all("""
        SELECT
            r.ReservationID AS reservation_id,
            r.ReservationPhoneNum AS user_phone_number,
            r.ReservationDateTime AS reserved_at,
            r.ReservationExpireDatetime AS expires_at,
            r.ReservationStatus AS status,

            t.TicketID AS ticket_id,
            t.TicketClass AS ticket_class,
            t.TicketPrice AS ticket_price,

            m.MatchID AS match_id,
            m.HomeTeam AS home_team,
            m.AwayTeam AS away_team,
            m.MatchDatetime AS match_datetime,

            (
                m.MatchDatetime <= CURRENT_TIMESTAMP
            ) AS match_started

        FROM Reservation AS r

        JOIN Ticket AS t
            ON t.TicketID = r.TicketID

        JOIN Matches AS m
            ON m.MatchID = t.MatchID

        WHERE r.ReservationStatus IN (
            'Reserved',
            'Paid'
        )

        ORDER BY r.ReservationDateTime DESC;
        """)

    suspicious_payments = fetch_all("""
        SELECT
            p.PaymentID AS payment_id,
            p.ReservationID AS reservation_id,
            p.PaymentAmount AS amount,
            p.PaymentMethod AS payment_method,
            p.PaymentDatetime AS payment_datetime,
            p.PaymentStatus AS payment_status,

            r.ReservationPhoneNum AS user_phone_number,
            r.ReservationStatus AS reservation_status

        FROM Payment AS p

        JOIN Reservation AS r
            ON r.ReservationID = p.ReservationID

        WHERE p.PaymentStatus IN (
            'Failed',
            'Pending'
        )

        ORDER BY p.PaymentDatetime DESC;
        """)

    user_reports = fetch_all("""
        SELECT
            rp.ReportID AS report_id,
            rp.ReservationID AS reservation_id,
            rp.SubmitterPhoneNum AS submitter_phone_number,
            rp.ReportCategory AS category,
            rp.ReportDescription AS description,
            rp.ReportStatus AS status,

            r.ReservationStatus AS reservation_status,

            t.TicketID AS ticket_id,

            m.HomeTeam AS home_team,
            m.AwayTeam AS away_team,
            m.MatchDatetime AS match_datetime

        FROM Report AS rp

        JOIN Reservation AS r
            ON r.ReservationID = rp.ReservationID

        JOIN Ticket AS t
            ON t.TicketID = r.TicketID

        JOIN Matches AS m
            ON m.MatchID = t.MatchID

        ORDER BY
            CASE
                WHEN rp.ReportStatus = 'Pending'
                    THEN 0
                ELSE 1
            END,
            rp.ReportID DESC;
        """)

    return {
        "cancelled_tickets": cancelled_tickets,
        "manageable_reservations": manageable_reservations,
        "suspicious_payments": suspicious_payments,
        "user_reports": user_reports,
    }


def cancel_reservation_by_support(
    reservation_id: int,
    support_phone_number: str,
) -> dict[str, Any]:
    """
    Cancel a reservation by a support user.

    Reserved:
        Cancel and restore capacity.

    Paid:
        Cancel, restore capacity, calculate the cancellation
        refund, and add the refund to the spectator's wallet.
    """

    with database_transaction():
        validate_support(support_phone_number)

        reservation = fetch_one(
            """
            SELECT
                r.ReservationID AS reservation_id,
                r.ReservationPhoneNum AS user_phone_number,
                r.ReservationStatus AS reservation_status,

                t.TicketID AS ticket_id,
                t.MatchID AS match_id,

                m.HomeTeam AS home_team,
                m.AwayTeam AS away_team,
                m.MatchDatetime AS match_datetime,
                (m.MatchDatetime <= CURRENT_TIMESTAMP) AS match_started,

                (
                    SELECT p.PaymentAmount
                    FROM Payment AS p
                    WHERE p.ReservationID = r.ReservationID
                      AND p.PaymentStatus = 'Success'
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
            raise SupportError(
                "RESERVATION_NOT_FOUND",
                "The requested reservation does not exist.",
            )

        if reservation["reservation_status"] == "Cancelled":
            raise SupportError(
                "RESERVATION_ALREADY_CANCELLED",
                "This reservation has already been cancelled.",
            )

        if reservation["reservation_status"] not in (
            "Reserved",
            "Paid",
        ):
            raise SupportError(
                "INVALID_RESERVATION_STATUS",
                "This reservation cannot be cancelled.",
            )

        if reservation["match_started"]:
            raise SupportError(
                "MATCH_STARTED",
                "The reservation cannot be cancelled after the match has started.",
            )

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
            [reservation["match_id"]],
        )

        if not match_tickets:
            raise RuntimeError("No tickets were found for this match.")

        capacities = {ticket["remained_capacity"] for ticket in match_tickets}

        if len(capacities) != 1:
            raise RuntimeError(
                "The remaining capacities for this match " "are not synchronized."
            )

        current_capacity = next(iter(capacities))

        refund = None

        if reservation["reservation_status"] == "Paid":
            if reservation["paid_amount"] is None:
                raise SupportError(
                    "SUCCESSFUL_PAYMENT_NOT_FOUND",
                    "No successful payment was found for this reservation.",
                )

            penalty = calculate_cancellation_penalty(
                match_datetime=reservation["match_datetime"],
                paid_amount=reservation["paid_amount"],
            )

            if not penalty["can_cancel"]:
                raise SupportError(
                    "MATCH_STARTED",
                    (
                        "The reservation cannot be cancelled "
                        "after the match has started."
                    ),
                )

            wallet = execute_returning(
                """
                UPDATE Users
                SET WalletBalance =
                    WalletBalance + %s
                WHERE PhoneNumber = %s
                RETURNING
                    WalletBalance AS wallet_balance;
                """,
                [
                    penalty["refund_amount"],
                    reservation["user_phone_number"],
                ],
            )

            if wallet is None:
                raise RuntimeError(
                    "The refund could not be added to the user's wallet."
                )

            refund = {
                "paid_amount": reservation["paid_amount"],
                "penalty_percentage": penalty["penalty_percentage"],
                "penalty_amount": penalty["penalty_amount"],
                "refund_amount": penalty["refund_amount"],
                "wallet_balance": wallet["wallet_balance"],
            }

        cancelled_reservation = execute_returning(
            """
            UPDATE Reservation
            SET
                ReservationStatus = 'Cancelled',
                CancellationPhoneNum = %s
            WHERE ReservationID = %s
              AND ReservationStatus IN (
                  'Reserved',
                  'Paid'
              )
            RETURNING
                ReservationID AS reservation_id,
                TicketID AS ticket_id,
                ReservationPhoneNum AS user_phone_number,
                CancellationPhoneNum AS cancelled_by,
                ReservationStatus AS status;
            """,
            [
                support_phone_number,
                reservation_id,
            ],
        )

        if cancelled_reservation is None:
            raise RuntimeError("The reservation could not be cancelled.")

        updated_count = execute(
            """
            UPDATE Ticket
            SET RemainedCapacity =
                RemainedCapacity + 1
            WHERE MatchID = %s;
            """,
            [reservation["match_id"]],
        )

        if updated_count != len(match_tickets):
            raise RuntimeError("Not all ticket capacities were restored.")

        return {
            "reservation": cancelled_reservation,
            "match": {
                "match_id": reservation["match_id"],
                "home_team": reservation["home_team"],
                "away_team": reservation["away_team"],
                "match_datetime": reservation["match_datetime"],
            },
            "refund": refund,
            "remained_capacity": current_capacity + 1,
        }
