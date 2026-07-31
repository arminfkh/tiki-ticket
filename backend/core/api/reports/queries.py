from core.common.database import execute_returning, fetch_one

GET_REPORT_CONTEXT_SQL = """
    SELECT
        u.PhoneNumber AS phone_number,
        u.AccountStatus AS account_status,
        u.UserRole AS role,

        r.ReservationID AS reservation_id,
        r.ReservationStatus AS reservation_status,

        t.TicketID AS ticket_id,
        t.TicketClass AS ticket_class,

        m.HomeTeam AS home_team,
        m.AwayTeam AS away_team,
        m.MatchDatetime AS match_datetime

    FROM Users AS u

    LEFT JOIN Reservation AS r
        ON r.ReservationPhoneNum = u.PhoneNumber
        AND r.ReservationID = %s

    LEFT JOIN Ticket AS t
        ON t.TicketID = r.TicketID

    LEFT JOIN Matches AS m
        ON m.MatchID = t.MatchID

    WHERE u.PhoneNumber = %s;
"""


CREATE_REPORT_SQL = """
    INSERT INTO Report (
        ReservationID,
        SubmitterPhoneNum,
        ReportCategory,
        ReportDescription,
        ReportStatus
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        'Pending'
    )
    RETURNING
        ReportID AS report_id,
        ReservationID AS reservation_id,
        SubmitterPhoneNum AS submitter_phone_number,
        ReportCategory AS category,
        ReportDescription AS description,
        ReportStatus AS status;
"""


def get_report_context(
    *,
    reservation_id: int,
    phone_number: str,
) -> dict | None:
    """
    Find the authenticated user and one reservation owned by them.
    """
    return fetch_one(
        GET_REPORT_CONTEXT_SQL,
        [
            reservation_id,
            phone_number,
        ],
    )


def create_report(
    *,
    reservation_id: int,
    phone_number: str,
    category: str,
    description: str,
) -> dict | None:
    """
    Create a pending report.
    """
    return execute_returning(
        CREATE_REPORT_SQL,
        [
            reservation_id,
            phone_number,
            category,
            description,
        ],
    )
