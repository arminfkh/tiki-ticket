-- -- 1) Receive a user’s email or phone number and show their purchased tickets ordered by purchase time.

-- CREATE OR REPLACE FUNCTION get_user_purchased_tickets(
--     p_user_identifier TEXT
-- )
-- RETURNS TABLE (
--     reservation_id     INT,
--     ticket_id          INT,

--     seat_number        VARCHAR(10),
--     seat_row           VARCHAR(10),
--     seat_section       VARCHAR(50),
--     ticket_class       VARCHAR(50),
--     ticket_price       NUMERIC(11, 3),

--     match_id           INT,
--     sport_type         VARCHAR(50),
--     home_team          VARCHAR(100),
--     away_team          VARCHAR(100),
--     match_datetime     TIMESTAMP,
--     league_name        VARCHAR(100),

--     venue_name         VARCHAR(150),
--     venue_city         VARCHAR(100),

--     purchase_datetime  TIMESTAMP
-- )

-- AS $$

--     WITH SelectedUser AS (
--         SELECT u.PhoneNumber
--         FROM Users AS u
--         WHERE u.PhoneNumber = p_user_identifier
--            OR LOWER(u.Email) = LOWER(p_user_identifier)
--     ),
--     SuccessfulPayments AS (
--         SELECT
--             p.ReservationID,
--             MIN(p.PaymentDatetime) AS PurchaseDatetime
--         FROM Payment AS p
--         WHERE p.PaymentStatus = 'Success'
--         GROUP BY p.ReservationID
--     )
--     SELECT
--         r.ReservationID,
--         t.TicketID,

--         t.SeatNumber,
--         t.SeatRow,
--         t.SeatSection,
--         t.TicketClass,
--         t.TicketPrice,

--         m.MatchID,
--         m.SportType,
--         m.HomeTeam,
--         m.AwayTeam,
--         m.MatchDatetime,
--         m.LeagueName,

--         v.VenueName,
--         v.VenueCity,

--         sp.PurchaseDatetime
--     FROM Reservation AS r
--     JOIN SelectedUser AS su
--         ON su.PhoneNumber = r.ReservationPhoneNum
--     JOIN SuccessfulPayments AS sp
--         ON sp.ReservationID = r.ReservationID
--     JOIN Ticket AS t
--         ON t.TicketID = r.TicketID
--     JOIN Matches AS m
--         ON m.MatchID = t.MatchID
--     JOIN Venue AS v
--         ON v.VenueID = m.VenueID
--     WHERE r.ReservationStatus = 'Paid'

--     ORDER BY sp.PurchaseDatetime DESC;
-- $$
-- LANGUAGE SQL


-- -- 2) Given a support staff member’s email or phone number, list users whose reservations were cancelled at least once.

-- CREATE OR REPLACE FUNCTION get_users_cancelled_by_support(
--     p_support_identifier TEXT
-- )
-- RETURNS TABLE (
--     customer_phone      VARCHAR(11),
--     customer_first_name VARCHAR(50),
--     customer_last_name  VARCHAR(50),
--     customer_email      VARCHAR(255)
-- )

-- AS $$

--     WITH SelectedSupport AS (
--         SELECT u.PhoneNumber
--         FROM Users AS u
--         WHERE (
--                 u.PhoneNumber = p_support_identifier
--                 OR LOWER(u.Email) = LOWER(p_support_identifier)
--               )
--           AND u.UserRole = 'Support'
--     )
--     SELECT DISTINCT
--         customer.PhoneNumber,
--         customer.FirstName,
--         customer.LastName,
--         customer.Email
--     FROM Reservation AS r
--     JOIN SelectedSupport AS ss
--         ON ss.PhoneNumber = r.CancellationPhoneNum
--     JOIN Users AS customer
--         ON customer.PhoneNumber = r.ReservationPhoneNum
--     WHERE r.ReservationStatus = 'Cancelled';
-- $$
-- LANGUAGE SQL


-- -- 3) Given a city name, list the tickets purchased in that city.

-- CREATE OR REPLACE FUNCTION get_purchased_tickets_by_city(
--     p_city_name TEXT
-- )
-- RETURNS TABLE (
--     reservation_id     INT,
--     ticket_id          INT,
--     buyer_phone        VARCHAR(11),
--     buyer_first_name   VARCHAR(50),
--     buyer_last_name    VARCHAR(50),
--     ticket_class       VARCHAR(50),
--     ticket_price       DECIMAL(11, 3),
--     seat_number        VARCHAR(10),
--     seat_row           VARCHAR(10),
--     seat_section       VARCHAR(50),
--     match_id           INT,
--     home_team          VARCHAR(100),
--     away_team          VARCHAR(100),
--     match_datetime     TIMESTAMP,
--     venue_name         VARCHAR(150)
-- )

-- AS $$

--     SELECT
--         r.ReservationID,
--         t.TicketID,
--         buyer.PhoneNumber,
--         buyer.FirstName,
--         buyer.LastName,
--         t.TicketClass,
--         t.TicketPrice,
--         t.SeatNumber,
--         t.SeatRow,
--         t.SeatSection,
--         m.MatchID,
--         m.HomeTeam,
--         m.AwayTeam,
--         m.MatchDatetime,
--         v.VenueName

--     FROM Reservation AS r
--     JOIN Users AS buyer
--         ON buyer.PhoneNumber = r.ReservationPhoneNum
--     JOIN Ticket AS t
--         ON t.TicketID = r.TicketID
--     JOIN Matches AS m
--         ON m.MatchID = t.MatchID
--     JOIN Venue AS v
--         ON v.VenueID = m.VenueID
--     WHERE r.ReservationStatus = 'Paid'
--       AND LOWER(v.VenueCity) = LOWER(p_city_name)
-- $$
-- LANGUAGE SQL;


-- -- 4) Given a search term, return tickets where it appears in the spectator’s name, team names, venue, or ticket category.

-- CREATE OR REPLACE FUNCTION search_purchased_tickets(
--     p_search_text TEXT
-- )
-- RETURNS TABLE (
--     ticket_id       INT,
--     seat_number     VARCHAR(10),
--     seat_row        VARCHAR(10),
--     seat_section    VARCHAR(50),
--     ticket_class    VARCHAR(50),
--     ticket_price    NUMERIC(11, 3),
--     facilities      JSONB,

--     sport_type      VARCHAR(50),
--     home_team       VARCHAR(100),
--     away_team       VARCHAR(100),
--     match_datetime  TIMESTAMP,
--     league_name     VARCHAR(100),

--     venue_name      VARCHAR(150),
--     venue_city      VARCHAR(100)
-- )
-- AS $$
--     SELECT
--         t.TicketID,
--         t.SeatNumber,
--         t.SeatRow,
--         t.SeatSection,
--         t.TicketClass,
--         t.TicketPrice,
--         t.Facilities,

--         m.SportType,
--         m.HomeTeam,
--         m.AwayTeam,
--         m.MatchDatetime,
--         m.LeagueName,

--         v.VenueName,
--         v.VenueCity
--     FROM Reservation AS r
--     JOIN Users AS spectator
--         ON spectator.PhoneNumber = r.ReservationPhoneNum
--     JOIN Ticket AS t
--         ON t.TicketID = r.TicketID
--     JOIN Matches AS m
--         ON m.MatchID = t.MatchID
--     JOIN Venue AS v
--         ON v.VenueID = m.VenueID
--     WHERE r.ReservationStatus = 'Paid'

--       AND (
--           spectator.FirstName
--               ILIKE '%' || TRIM(p_search_text) || '%'

--           OR spectator.LastName
--               ILIKE '%' || TRIM(p_search_text) || '%'

--           OR CONCAT_WS(
--                  ' ',
--                  spectator.FirstName,
--                  spectator.LastName
--              ) ILIKE '%' || TRIM(p_search_text) || '%'

--           OR m.HomeTeam
--               ILIKE '%' || TRIM(p_search_text) || '%'

--           OR m.AwayTeam
--               ILIKE '%' || TRIM(p_search_text) || '%'

--           OR v.VenueName
--               ILIKE '%' || TRIM(p_search_text) || '%'

--           OR t.TicketClass
--               ILIKE '%' || TRIM(p_search_text) || '%'
--       )
-- $$
-- LANGUAGE SQL;


-- -- 5) Given a user’s phone number or email, display other users who live in the same city.

-- CREATE OR REPLACE FUNCTION get_users_in_same_city(
--     p_user_identifier TEXT
-- )
-- RETURNS TABLE (
--     phone_number   VARCHAR(11),
--     email          VARCHAR(255),
--     first_name     VARCHAR(50),
--     last_name      VARCHAR(50),
--     residence_city VARCHAR(100)
-- )
-- AS $$
--     WITH SelectedUser AS (
--         SELECT
--             u.PhoneNumber,
--             u.ResidenceCity
--         FROM Users AS u
--         WHERE u.PhoneNumber = p_user_identifier
--            OR LOWER(u.Email) = LOWER(TRIM(p_user_identifier))
--     )
--     SELECT
--         other_user.PhoneNumber,
--         other_user.Email,
--         other_user.FirstName,
--         other_user.LastName,
--         other_user.ResidenceCity
--     FROM Users AS other_user
--     JOIN SelectedUser AS selected_user
--         ON LOWER(other_user.ResidenceCity)
--            = LOWER(selected_user.ResidenceCity)
--     WHERE other_user.PhoneNumber <> selected_user.PhoneNumber
-- $$
-- LANGUAGE SQL;


-- 6) Given a date and a number n, display the top n users with the most ticket purchases since that date.

CREATE OR REPLACE FUNCTION get_top_ticket_buyers(
    p_start_date DATE,
    p_n          INT
)
RETURNS TABLE (
    phone_number   VARCHAR(11),
    email          VARCHAR(255),
    first_name     VARCHAR(50),
    last_name      VARCHAR(50),
    purchase_count INT
)
AS $$
    WITH SuccessfulPurchases AS (
        SELECT
            p.ReservationID,
            MIN(p.PaymentDatetime) AS PurchaseDatetime
        FROM Payment AS p
        WHERE p.PaymentStatus = 'Success'
        GROUP BY p.ReservationID
    )
    SELECT
        u.PhoneNumber,
        u.Email,
        u.FirstName,
        u.LastName,
        COUNT(*) AS PurchaseCount
    FROM Users AS u
    JOIN Reservation AS r
        ON r.ReservationPhoneNum = u.PhoneNumber
    JOIN SuccessfulPurchases AS sp
        ON sp.ReservationID = r.ReservationID
    WHERE r.ReservationStatus = 'Paid'
      AND sp.PurchaseDatetime >= p_start_date
      AND p_n > 0
    GROUP BY
        u.PhoneNumber,
        u.Email,
        u.FirstName,
        u.LastName

    LIMIT p_n;
$$
LANGUAGE SQL;


-- -- 7) Given a sport type, list its cancelled tickets ordered by match date.

-- CREATE FUNCTION get_cancelled_tickets_by_sport(
--     p_sport_type TEXT
-- )
-- RETURNS TABLE (
--     reservation_id INT,
--     ticket_id       INT,
--     seat_number     VARCHAR(10),
--     seat_row        VARCHAR(10),
--     seat_section    VARCHAR(50),
--     ticket_class    VARCHAR(50),
--     ticket_price    NUMERIC(11, 3),
--     facilities      JSONB,
--     home_team       VARCHAR(100),
--     away_team       VARCHAR(100),
--     match_datetime  TIMESTAMP,
--     league_name     VARCHAR(100),
--     venue_name      VARCHAR(150)
-- )
-- AS $$
--     SELECT
--         r.ReservationID,
--         t.TicketID,
--         t.SeatNumber,
--         t.SeatRow,
--         t.SeatSection,
--         t.TicketClass,
--         t.TicketPrice,
--         t.Facilities,
--         m.HomeTeam,
--         m.AwayTeam,
--         m.MatchDatetime,
--         m.LeagueName,
--         v.VenueName
--     FROM Reservation AS r
--     JOIN Ticket AS t
--         ON t.TicketID = r.TicketID
--     JOIN Matches AS m
--         ON m.MatchID = t.MatchID
--     JOIN Venue AS v
--         ON v.VenueID = m.VenueID
--     WHERE r.ReservationStatus = 'Cancelled'
--       AND LOWER(m.SportType) = LOWER(TRIM(p_sport_type))
--     ORDER BY m.MatchDatetime DESC;
-- $$
-- LANGUAGE SQL;


-- 8) Given a report subject, list the users with the most reports on that subject.

CREATE FUNCTION get_top_reporters_by_subject(
    p_report_subject TEXT
)
RETURNS TABLE (
    phone_number VARCHAR(11),
    email        VARCHAR(255),
    first_name   VARCHAR(50),
    last_name    VARCHAR(50),
    report_count INT
)
AS $$
    WITH ReportCounts AS (
        SELECT
            u.PhoneNumber,
            u.Email,
            u.FirstName,
            u.LastName,
            COUNT(rp.ReportID) AS ReportCount
        FROM Report AS rp
        JOIN Users AS u
            ON u.PhoneNumber = rp.SubmitterPhoneNum
        WHERE LOWER(TRIM(rp.ReportCategory))
              = LOWER(TRIM(p_report_subject))
        GROUP BY
            u.PhoneNumber,
            u.Email,
            u.FirstName,
            u.LastName
    )
    SELECT
        rc.PhoneNumber,
        rc.Email,
        rc.FirstName,
        rc.LastName,
        rc.ReportCount
    FROM ReportCounts AS rc
    WHERE rc.ReportCount = (
        SELECT MAX(rc2.ReportCount)
        FROM ReportCounts AS rc2
    )

$$
LANGUAGE SQL;