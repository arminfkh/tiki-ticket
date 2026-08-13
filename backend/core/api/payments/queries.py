from typing import Any

from core.common.database import (
    database_transaction,
    execute,
    execute_returning,
    fetch_all,
    fetch_one,
)


class PaymentError(Exception):
    """
    An expected payment-related error.
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
        raise PaymentError(
            "USER_NOT_FOUND",
            "No user was found with this phone number.",
        )

    if user["account_status"] != "Active":
        raise PaymentError(
            "USER_INACTIVE",
            "The user account is inactive.",
        )

    if user["user_role"] != "Spectator":
        raise PaymentError(
            "USER_NOT_SPECTATOR",
            "Only spectator accounts can make ticket payments.",
        )


def process_payment(
    reservation_id: int,
    phone_number: str,
    payment_method: str,
    payment_status: str,
) -> dict[str, Any]:
    """
    Record a payment attempt for an active reservation.

    Successful payment:
        Reservation becomes Paid.

    Failed payment:
        Reservation remains Reserved.

    Wallet payment:
        The user's wallet balance is checked and locked.
        If the balance is sufficient, the ticket price is deducted
        and the payment is completed successfully.
    """

    error_after_commit: PaymentError | None = None
    result: dict[str, Any] | None = None

    with database_transaction():
        validate_spectator(phone_number)

        # Read the match ID before locking all ticket rows.
        reservation_preview = fetch_one(
            """
            SELECT
                r.ReservationID AS reservation_id,
                t.MatchID AS match_id
            FROM Reservation AS r
            JOIN Ticket AS t
                ON t.TicketID = r.TicketID
            WHERE r.ReservationID = %s;
            """,
            [reservation_id],
        )

        if reservation_preview is None:
            raise PaymentError(
                "RESERVATION_NOT_FOUND",
                "The requested reservation does not exist.",
            )

        match_id = reservation_preview["match_id"]

        # Use the same lock order as the reservation API:
        # first lock ticket rows, then lock the reservation.
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
            raise RuntimeError("No ticket rows were found for this match.")

        capacities = {ticket["remained_capacity"] for ticket in match_tickets}

        if len(capacities) != 1:
            raise RuntimeError(
                "The remaining capacities for this match are not synchronized."
            )

        reservation = fetch_one(
            """
            SELECT
                r.ReservationID AS reservation_id,
                r.ReservationPhoneNum AS phone_number,
                r.ReservationStatus AS reservation_status,
                r.ReservationDateTime AS reserved_at,
                r.ReservationExpireDatetime AS expires_at,

                t.TicketID AS ticket_id,
                t.TicketPrice AS ticket_price,
                t.TicketClass AS ticket_class,
                t.SeatNumber AS seat_number,
                t.SeatRow AS seat_row,
                t.SeatSection AS seat_section,

                m.MatchID AS match_id,
                m.HomeTeam AS home_team,
                m.AwayTeam AS away_team,
                m.MatchDatetime AS match_datetime,

                (
                    r.ReservationExpireDatetime
                    <= CURRENT_TIMESTAMP
                ) AS is_expired,

                (
                    m.MatchDatetime
                    <= CURRENT_TIMESTAMP
                ) AS match_started,

                GREATEST(
                    EXTRACT(
                        EPOCH FROM (
                            r.ReservationExpireDatetime
                            - CURRENT_TIMESTAMP
                        )
                    )::INT,
                    0
                ) AS remaining_seconds

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
            raise PaymentError(
                "RESERVATION_NOT_FOUND",
                "The requested reservation does not exist.",
            )

        if reservation["phone_number"] != phone_number:
            raise PaymentError(
                "RESERVATION_NOT_OWNED",
                "This reservation belongs to another user.",
            )

        if reservation["reservation_status"] == "Paid":
            raise PaymentError(
                "RESERVATION_ALREADY_PAID",
                "This reservation has already been paid.",
            )

        if reservation["reservation_status"] == "Cancelled":
            raise PaymentError(
                "RESERVATION_CANCELLED",
                "A cancelled reservation cannot be paid.",
            )

        # The cancellation must be committed even though the API
        # later returns an error response.
        if reservation["is_expired"]:
            execute(
                """
                UPDATE Reservation
                SET ReservationStatus = 'Cancelled'
                WHERE ReservationID = %s;
                """,
                [reservation_id],
            )

            execute(
                """
                UPDATE Ticket
                SET RemainedCapacity =
                    RemainedCapacity + 1
                WHERE MatchID = %s;
                """,
                [match_id],
            )

            error_after_commit = PaymentError(
                "RESERVATION_EXPIRED",
                "The reservation expired before payment.",
            )

        elif reservation["match_started"]:
            execute(
                """
                UPDATE Reservation
                SET ReservationStatus = 'Cancelled'
                WHERE ReservationID = %s;
                """,
                [reservation_id],
            )

            execute(
                """
                UPDATE Ticket
                SET RemainedCapacity =
                    RemainedCapacity + 1
                WHERE MatchID = %s;
                """,
                [match_id],
            )

            error_after_commit = PaymentError(
                "MATCH_STARTED",
                "Payment is not allowed after the match has started.",
            )

        else:
            successful_payment = fetch_one(
                """
                SELECT
                    PaymentID AS payment_id
                FROM Payment
                WHERE ReservationID = %s
                  AND PaymentStatus = 'Success'
                LIMIT 1;
                """,
                [reservation_id],
            )

            if successful_payment is not None:
                raise PaymentError(
                    "PAYMENT_ALREADY_SUCCESSFUL",
                    "A successful payment already exists for this reservation.",
                )

            wallet_balance = None

            if payment_method == "Wallet":
                wallet = fetch_one(
                    """
                    SELECT
                        WalletBalance AS wallet_balance
                    FROM Users
                    WHERE PhoneNumber = %s
                    FOR UPDATE;
                    """,
                    [phone_number],
                )

                if wallet is None:
                    raise PaymentError(
                        "USER_NOT_FOUND",
                        "No user was found with this phone number.",
                    )

                if wallet["wallet_balance"] < reservation["ticket_price"]:
                    raise PaymentError(
                        "INSUFFICIENT_WALLET_BALANCE",
                        (
                            "The wallet balance is not enough "
                            "to complete this payment."
                        ),
                    )

                updated_wallet = execute_returning(
                    """
                    UPDATE Users
                    SET WalletBalance = WalletBalance - %s
                    WHERE PhoneNumber = %s
                    RETURNING
                        WalletBalance AS wallet_balance;
                    """,
                    [
                        reservation["ticket_price"],
                        phone_number,
                    ],
                )

                if updated_wallet is None:
                    raise RuntimeError("The wallet balance could not be updated.")

                wallet_balance = updated_wallet["wallet_balance"]

                # A wallet payment succeeds when sufficient balance exists.
                payment_status = "Success"

            payment = execute_returning(
                """
                INSERT INTO Payment (
                    ReservationID,
                    PaymentAmount,
                    PaymentMethod,
                    PaymentDatetime,
                    PaymentStatus
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    %s
                )
                RETURNING
                    PaymentID AS payment_id,
                    ReservationID AS reservation_id,
                    PaymentAmount AS amount,
                    PaymentMethod AS method,
                    PaymentDatetime AS payment_datetime,
                    PaymentStatus AS status;
                """,
                [
                    reservation_id,
                    reservation["ticket_price"],
                    payment_method,
                    payment_status,
                ],
            )

            if payment is None:
                raise RuntimeError("PostgreSQL did not return the created payment.")

            if payment_method == "Wallet":
                payment["wallet_balance"] = wallet_balance

            if payment_status == "Success":
                updated_reservation = execute_returning(
                    """
                    UPDATE Reservation
                    SET ReservationStatus = 'Paid'
                    WHERE ReservationID = %s
                      AND ReservationStatus = 'Reserved'
                    RETURNING
                        ReservationID AS reservation_id,
                        ReservationStatus AS status;
                    """,
                    [reservation_id],
                )

                if updated_reservation is None:
                    raise RuntimeError("The reservation could not be marked as paid.")

                result = {
                    "payment": payment,
                    "issued_ticket": {
                        "reservation_id": reservation_id,
                        "ticket_id": reservation["ticket_id"],
                        "phone_number": phone_number,
                        "status": "Paid",
                        "ticket_class": reservation["ticket_class"],
                        "seat_number": reservation["seat_number"],
                        "seat_row": reservation["seat_row"],
                        "seat_section": reservation["seat_section"],
                        "match_id": reservation["match_id"],
                        "home_team": reservation["home_team"],
                        "away_team": reservation["away_team"],
                        "match_datetime": reservation["match_datetime"],
                    },
                }

            else:
                result = {
                    "payment": payment,
                    "reservation": {
                        "reservation_id": reservation_id,
                        "ticket_id": reservation["ticket_id"],
                        "status": "Reserved",
                        "expires_at": reservation["expires_at"],
                        "remaining_seconds": reservation["remaining_seconds"],
                    },
                }

    # Raising this outside the transaction keeps the cancellation
    # and restored capacity committed.
    if error_after_commit is not None:
        raise error_after_commit

    if result is None:
        raise RuntimeError("The payment operation did not return a result.")

    return result
