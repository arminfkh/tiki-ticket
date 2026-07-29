-- reset database

DROP TABLE IF EXISTS ReportRev CASCADE;
DROP TABLE IF EXISTS Report CASCADE;
DROP TABLE IF EXISTS Payment CASCADE;
DROP TABLE IF EXISTS Reservation CASCADE;
DROP TABLE IF EXISTS Ticket CASCADE;
DROP TABLE IF EXISTS Matches CASCADE;
DROP TABLE IF EXISTS Venue CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

DROP FUNCTION IF EXISTS get_user_purchased_tickets(TEXT);
DROP FUNCTION IF EXISTS get_users_cancelled_by_support(TEXT);
DROP FUNCTION IF EXISTS get_purchased_tickets_by_city(TEXT);
DROP FUNCTION IF EXISTS search_purchased_tickets(TEXT);
DROP FUNCTION IF EXISTS get_users_in_same_city(TEXT);
DROP FUNCTION IF EXISTS get_top_ticket_buyers(TEXT);
DROP FUNCTION IF EXISTS get_cancelled_tickets_by_sport(TEXT);
DROP FUNCTION IF EXISTS get_top_reporters_by_subject(TEXT);


-- create tables

CREATE TABLE Users (
	PhoneNumber VARCHAR(11) PRIMARY KEY,
	Email VARCHAR(255) UNIQUE NOT NULL,
	FirstName VARCHAR(50) NOT NULL,
	LastName VARCHAR(50) NOT NULL,
	ResidenceCity VARCHAR(100),
	HashedPassword VARCHAR(255) NOT NULL,
	SignUpDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	AccountStatus VARCHAR(20) CHECK (AccountStatus IN ('Active', 'Inactive')),
	UserRole VARCHAR(20) CHECK (UserRole IN ('Spectator', 'Support'))	
);

CREATE TABLE Venue (
    VenueID SERIAL PRIMARY KEY,
    VenueCity VARCHAR(100) NOT NULL,
    VenueName VARCHAR(150) NOT NULL,
    Capacity INT CHECK (Capacity > 0)
);

CREATE TABLE Matches (
    MatchID SERIAL PRIMARY KEY,
    VenueID INT REFERENCES Venue(VenueID) ON DELETE CASCADE,
    SportType VARCHAR(50) CHECK (SportType IN ('Football', 'Volleyball', 'Basketball')),
    HomeTeam VARCHAR(100) NOT NULL,
    AwayTeam VARCHAR(100) NOT NULL,
    MatchDatetime TIMESTAMP NOT NULL,
    LeagueName VARCHAR(100) NOT NULL
);

CREATE TABLE Ticket (
    TicketID SERIAL PRIMARY KEY,
    MatchID INT REFERENCES Matches(MatchID) ON DELETE CASCADE,
    SeatNumber VARCHAR(10),
    SeatRow VARCHAR(10),
    SeatSection VARCHAR(50),
    TicketClass VARCHAR(50) CHECK (TicketClass IN ('Regular', 'Premium', 'VIP')) DEFAULT 'Regular',
    TicketPrice DECIMAL(11, 3) CHECK (TicketPrice >= 0),
    RemainedCapacity INT CHECK (RemainedCapacity >= 0),
    Facilities JSONB
);

CREATE TABLE Reservation (
    ReservationID SERIAL PRIMARY KEY,
    TicketID INT REFERENCES Ticket(TicketID) ON DELETE CASCADE,
    ReservationPhoneNum VARCHAR(11) REFERENCES Users(PhoneNumber) ON DELETE CASCADE,
    CancellationPhoneNum VARCHAR(11) REFERENCES Users(PhoneNumber) ON DELETE SET NULL,
    ReservationDateTime TIMESTAMP NOT NULL,
    ReservationExpireDatetime TIMESTAMP,
    ReservationStatus VARCHAR(20) CHECK (ReservationStatus IN ('Reserved', 'Paid', 'Cancelled')),
    CONSTRAINT chk_expire_date CHECK (ReservationExpireDatetime >= ReservationDateTime)
);

CREATE TABLE Payment (
    PaymentID SERIAL PRIMARY KEY,
    ReservationID INT REFERENCES Reservation(ReservationID) ON DELETE SET NULL,
    PaymentAmount DECIMAL(11, 3) CHECK (PaymentAmount >= 0),
    PaymentMethod VARCHAR(50),
    PaymentDatetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PaymentStatus VARCHAR(20) CHECK (PaymentStatus IN ('Success', 'Failed', 'Pending')) DEFAULT 'Pending'
);

CREATE TABLE Report (
    ReportID SERIAL PRIMARY KEY,
    ReservationID INT REFERENCES Reservation(ReservationID) ON DELETE CASCADE,
    SubmitterPhoneNum VARCHAR(11) REFERENCES Users(PhoneNumber) ON DELETE CASCADE,
    ReportCategory VARCHAR(100),
    ReportDescription TEXT,
    ReportStatus VARCHAR(20) CHECK (ReportStatus IN ('Pending', 'Reviewed'))
);

CREATE TABLE ReportRev (
    ReportID INT REFERENCES Report(ReportID) ON DELETE CASCADE,
    ReviewerPhoneNum VARCHAR(11) REFERENCES Users(PhoneNumber) ON DELETE CASCADE,
    PRIMARY KEY (ReportID, ReviewerPhoneNum)
);

CREATE INDEX idx_match_sport ON MATCHES(SportType);
CREATE INDEX idx_match_datetime ON Matches(MatchDatetime);
CREATE INDEX idx_venue_city ON Venue(VenueCity);
CREATE INDEX idx_ticket_class ON Ticket(TicketClass);

CREATE INDEX idx_reservation_user ON Reservation(ReservationPhoneNum);
CREATE INDEX idx_ticket_match ON Ticket(MatchID);
CREATE INDEX idx_matches_venue ON Matches(VenueID);
CREATE INDEX idx_report_user ON Report(SubmitterPhoneNum);
CREATE INDEX idx_report_reservation ON Report(ReservationID);


-- Insert Users

    -- Galileo and Nikola intentionally have no reservations.

INSERT INTO Users
    (PhoneNumber, Email, FirstName, LastName, ResidenceCity,
     HashedPassword, SignUpDate, AccountStatus, UserRole)
VALUES
    -- Supports
    ('09901200111', 'alan.turing@example.com',       'Alan',    'Turing',      'London',   'hashed_password_support_01', '2024-03-10 09:15:00', 'Active',   'Support'),
    ('09901200222', 'grace.hopper@example.com',      'Grace',   'Hopper',      'London',   'hashed_password_support_02', '2024-08-14 10:45:00', 'Active',   'Support'),
    ('09901200333', 'ada.lovelace@example.com',      'Ada',     'Lovelace',    'London',   'hashed_password_support_03', '2024-04-12 11:30:00', 'Active',   'Support'),

    -- Spectators
    ('09901200001', 'linus.torvalds@example.com',    'Linus',   'Torvalds',    'Helsinki', 'hashed_password_user_01',    '2024-05-18 14:20:00', 'Active',   'Spectator'),
    ('09901200002', 'tim.berners-lee@example.com',   'Tim',     'Berners-Lee', 'Helsinki', 'hashed_password_user_02',    '2024-01-05 08:00:00', 'Active',   'Spectator'),
    ('09901200003', 'albert.einstein@example.com',   'Albert',  'Einstein',    'Warsaw',   'hashed_password_user_03',    '2024-06-25 16:10:00', 'Active',   'Spectator'),
    ('09901200004', 'isaac.newton@example.com',      'Isaac',   'Newton',      'London',   'hashed_password_user_04',    '2024-10-08 13:25:00', 'Active',   'Spectator'),
    ('09901200005', 'marie.curie@example.com',       'Marie',   'Curie',       'Warsaw',   'hashed_password_user_05',    '2025-01-15 09:40:00', 'Active',   'Spectator'),
    ('09901200006', 'richard.feynman@example.com',   'Richard', 'Feynman',     'New York', 'hashed_password_user_06',    '2025-03-22 12:05:00', 'Active',   'Spectator'),
    ('09901200007', 'louis.pasteur@example.com',     'Louis',   'Pasteur',     'Dole',     'hashed_password_user_07',    '2025-05-19 15:35:00', 'Active',   'Spectator'),
    ('09901200008', 'galileo.galilei@example.com',   'Galileo', 'Galilei',     'Paris',    'hashed_password_user_08',    '2025-07-07 17:20:00', 'Inactive', 'Spectator'),
    ('09901200009', 'nikola.tesla@example.com',      'Nikola',  'Tesla',       'New York', 'hashed_password_user_09',    '2025-09-11 11:55:00', 'Active',   'Spectator');


-- Insert Venues

    -- Venue IDs are explicit so later seed rows remain readable.

INSERT INTO Venue (VenueCity, VenueName, Capacity)
VALUES
    ('Tehran',         'Azadi Stadium',              80000), -- #1
    ('Tehran',         'Shahid Dastgerdi Stadium',    8250), -- #2
    ('Shemroon',       'Shemroon Boys Stadium',       4400), -- #3
    ('Damavand',       'Damavand Arena',             10000), -- #4
    ('London',         'Wembley Stadium',            90000), -- #5
    ('Barcelona',      'Camp Nou',                   60000), -- #6
    ('Madrid',         'Santiago Bernabeu Stadium',  80000), -- #7
    ('Munich',         'Allianz Arena',              75000), -- #8
    ('New York',       'Rucker Park',                20000), -- #9
    ('Rio de Janeiro', 'Copacabana Beach',           10000) -- #10
    ;


-- Insert Matches

INSERT INTO Matches
    (VenueID, SportType, HomeTeam, AwayTeam, MatchDatetime, LeagueName)
VALUES
    (1, 'Football',   'Esteghlal',       'Persepolis',
        CURRENT_DATE - 1 + TIME '20:00:00', 'Persian Gulf Pro League'),         -- #1

    (1, 'Volleyball', 'Iran',            'Japan',
        CURRENT_DATE + 10 + TIME '18:00:00', 'International Volleyball Cup'),   -- #2

    (2, 'Basketball', 'Tehran Lions',    'Isfahan Stars',
        CURRENT_DATE + 5 + TIME '19:00:00', 'Iran Basketball League'),          -- #3

    (3, 'Football',   'Shemroon Boys',   'Damavand United',
        CURRENT_DATE + 7 + TIME '17:30:00', 'Tehran Province League'),          -- #4

    (4, 'Volleyball', 'Damavand VC',     'Tehran VC',
        CURRENT_DATE + 8 + TIME '16:00:00', 'Iran Volleyball League'),          -- #5

    (5, 'Football',   'England',         'Germany',
        '2025-11-20 20:00:00', 'International Friendly'),                       -- #6

    (6, 'Football',   'Barcelona',       'Real Madrid',
        '2026-02-14 21:00:00', 'La Liga'),                                      -- #7

    (9, 'Basketball', 'Harlem Ballers',  'Brooklyn Kings',
        CURRENT_DATE + 15 + TIME '20:30:00', 'New York Street League'),         -- #8

    (8, 'Volleyball', 'Munich Eagles',   'Berlin Spikers',
        CURRENT_DATE + 25 + TIME '18:30:00', 'German Volleyball League')        -- #9
    ;


-- Insert Tickets

INSERT INTO Ticket
    (MatchID, SeatNumber, SeatRow, SeatSection,
     TicketClass, TicketPrice, RemainedCapacity, Facilities)
VALUES
    -- Match 1: Azadi, Football
    (1, '1', 'A', 'North', 'Regular',  50.000, 4000, '{"parking": true}'),                                  -- #1
    (1, '2', 'A', 'North', 'Regular',  50.000, 4000, '{"parking": true}'),                                  -- #2
    (1, '1', 'B', 'West',  'Premium',  80.000, 4000, '{"parking": true, "snack": true}'),                   -- #3
    (1, '1', 'V', 'VIP',   'VIP',     150.000, 4000, '{"parking": true, "snack": true, "lounge": true}'),   -- #4

    -- Match 2: Azadi, Volleyball
    (2, '1', 'A', 'East',  'Regular',  40.000, 4000, '{"parking": true}'),                                  -- #5
    (2, '1', 'B', 'West',  'Premium',  70.000, 4000, '{"parking": true, "snack": true}'),                   -- #6
    (2, '1', 'V', 'VIP',   'VIP',     130.000, 4000, '{"parking": true, "snack": true, "lounge": true}'),   -- #7

    -- Match 3: Shahid Dastgerdi, Basketball
    (3, '1', 'A', 'East',  'Regular',  35.000, 4000, '{"snack": true}'),                                    -- #8
    (3, '2', 'A', 'East',  'Regular',  35.000, 4000, '{"snack": true}'),                                    -- #9
    (3, '1', 'B', 'West',  'Premium',  60.000, 4000, '{"snack": true, "better_view": true}'),               -- #10

    -- Match 4: Shemroon, Football
    (4, '1', 'A', 'North', 'Regular',  45.000, 4000, '{"parking": false}'),                                 -- #11
    (4, '1', 'B', 'West',  'Premium',  75.000, 4000, '{"snack": true}'),                                    -- #12
    (4, '1', 'V', 'VIP',   'VIP',     140.000, 4000, '{"snack": true, "lounge": true}'),                    -- #13

    -- Match 5: Damavand, Volleyball
    (5, '1', 'A', 'East',  'Regular',  30.000, 4000, '{"parking": true}'),                                  -- #14
    (5, '2', 'A', 'East',  'Regular',  30.000, 4000, '{"parking": true}'),                                  -- #15
    (5, '1', 'B', 'West',  'Premium',  55.000, 4000, '{"parking": true, "snack": true}'),                   -- #16

    -- Match 6: Wembley, Football
    (6, '1', 'A', 'North', 'Regular',  90.000, 4000, '{"parking": true}'),                                  -- #17
    (6, '1', 'B', 'West',  'Premium', 150.000, 4000, '{"parking": true, "snack": true}'),                   -- #18
    (6, '1', 'V', 'VIP',   'VIP',     250.000, 4000, '{"parking": true, "snack": true, "lounge": true}'),   -- #19

    -- Match 7: Camp Nou, Football
    (7, '1', 'A', 'North', 'Regular', 100.000, 4000, '{"parking": true}'),                                  -- #20
    (7, '2', 'A', 'North', 'Regular', 100.000, 4000, '{"parking": true}'),                                  -- #21
    (7, '1', 'B', 'West',  'Premium', 180.000, 4000, '{"parking": true, "snack": true}'),                   -- #22

    -- Match 8: Rucker Park, Basketball
    (8, '1', 'A', 'Court', 'Regular',  25.000, 4000, '{"outdoor": true}'),                                  -- #23
    (8, '1', 'B', 'Court', 'Premium',  50.000, 4000, '{"outdoor": true, "front_row": true}'),               -- #24
    (8, '1', 'V', 'Court', 'VIP',     100.000, 4000, '{"outdoor": true, "front_row": true}'),               -- #25

    -- Match 9: Allianz Arena, Volleyball
    (9, '1', 'A', 'East',  'Regular',  45.000, 4000, '{"parking": true}'),                                  -- #26
    (9, '1', 'B', 'West',  'Premium',  75.000, 4000, '{"parking": true, "snack": true}'),                   -- #27
    (9, '1', 'V', 'VIP',   'VIP',     140.000, 4000, '{"parking": true, "snack": true, "lounge": true}')    -- #28
    ;


-- Insert Reservations

    -- Paid reservations always receive a successful payment below.
    -- Some cancelled reservations receive failed payments.
    -- Ticket 5, 6, 12, and 23 have failed attempts before later sales.

INSERT INTO Reservation
    (TicketID, ReservationPhoneNum, CancellationPhoneNum,
     ReservationDateTime, ReservationExpireDatetime, ReservationStatus)
VALUES
    -- Older successful purchases
    (17, '09901200002', NULL,
        '2025-10-01 10:00:00', '2025-10-01 10:15:00', 'Paid'),  -- #1

    (18, '09901200005', NULL,
        '2025-10-05 11:00:00', '2025-10-05 11:15:00', 'Paid'),  -- #2

    (20, '09901200002', NULL,
        '2026-01-20 09:00:00', '2026-01-20 09:15:00', 'Paid'),  -- #3

    (12, '09901200004', NULL,
        '2026-03-15 13:00:00', '2026-03-15 13:15:00', 'Paid'),  -- #4

    (14, '09901200004', NULL,
        '2026-04-10 14:00:00', '2026-04-10 14:15:00', 'Paid'),  -- #5

    (15, '09901200005', NULL,
        '2026-05-12 12:00:00', '2026-05-12 12:15:00', 'Paid'),  -- #6

    (23, '09901200005', NULL,
        '2026-06-18 16:00:00', '2026-06-18 16:15:00', 'Paid'),  -- #7

    -- Cancelled attempts
    (5, '09901200006', '09901200111',
        CURRENT_DATE - 8 + TIME '09:00:00',
        CURRENT_DATE - 8 + TIME '09:15:00', 'Cancelled'),       -- #8

    (6, '09901200006', '09901200111',
        CURRENT_DATE - 7 + TIME '10:00:00',
        CURRENT_DATE - 7 + TIME '10:15:00', 'Cancelled'),       -- #9

    (12, '09901200006', '09901200222',
        '2026-03-10 11:00:00', '2026-03-10 11:15:00', 'Cancelled'),  -- #10

    (23, '09901200006', '09901200111',
        '2026-06-15 10:00:00', '2026-06-15 10:15:00', 'Cancelled'),  -- #11

    (13, '09901200004', '09901200333',
        CURRENT_DATE - 12 + TIME '08:30:00',
        CURRENT_DATE - 12 + TIME '08:45:00', 'Cancelled'),      -- #12

    (24, '09901200004', '09901200222',
        CURRENT_DATE - 11 + TIME '09:30:00',
        CURRENT_DATE - 11 + TIME '09:45:00', 'Cancelled'),      -- #13

    (16, '09901200005', '09901200333',
        CURRENT_DATE - 10 + TIME '10:30:00',
        CURRENT_DATE - 10 + TIME '10:45:00', 'Cancelled'),      -- #14

    (26, '09901200002', '09901200111',
        CURRENT_DATE - 9 + TIME '11:30:00',
        CURRENT_DATE - 9 + TIME '11:45:00', 'Cancelled'),       -- #15

    -- Purchases in the last seven days
    (1, '09901200001', NULL,
        CURRENT_DATE - 1 + TIME '10:00:00',
        CURRENT_DATE - 1 + TIME '10:15:00', 'Paid'),  -- #16

    (5, '09901200001', NULL,
        CURRENT_DATE - 5 + TIME '11:00:00',
        CURRENT_DATE - 5 + TIME '11:15:00', 'Paid'),  -- #17

    (8, '09901200001', NULL,
        CURRENT_DATE - 4 + TIME '12:00:00',
        CURRENT_DATE - 4 + TIME '12:15:00', 'Paid'),  -- #18

    (11, '09901200001', NULL,
        CURRENT_DATE - 3 + TIME '13:00:00',
        CURRENT_DATE - 3 + TIME '13:15:00', 'Paid'),  -- #19

    (2, '09901200002', NULL,
        CURRENT_DATE - 1 + TIME '11:00:00',
        CURRENT_DATE - 1 + TIME '11:15:00', 'Paid'),  -- #20

    (6, '09901200002', NULL,
        CURRENT_DATE - 4 + TIME '14:00:00',
        CURRENT_DATE - 4 + TIME '14:15:00', 'Paid'),  -- #21

    (9, '09901200002', NULL,
        CURRENT_DATE - 2 + TIME '10:30:00',
        CURRENT_DATE - 2 + TIME '10:45:00', 'Paid'),  -- #22

    (3, '09901200003', NULL,
        CURRENT_DATE - 1 + TIME '12:00:00',
        CURRENT_DATE - 1 + TIME '12:15:00', 'Paid'),  -- #23

    (10, '09901200003', NULL,
        CURRENT_DATE - 1 + TIME '15:00:00',
        CURRENT_DATE - 1 + TIME '15:15:00', 'Paid'),  -- #24

    -- Today's successful purchases
    (7, '09901200007', NULL,
        CURRENT_DATE + TIME '18:00:00',
        CURRENT_DATE + TIME '18:15:00', 'Paid'),  -- #25

    (27, '09901200005', NULL,
        CURRENT_DATE + TIME '09:00:00',
        CURRENT_DATE + TIME '09:15:00', 'Paid'),  -- #26

    (28, '09901200004', NULL,
        CURRENT_DATE + TIME '13:00:00',
        CURRENT_DATE + TIME '13:15:00', 'Paid'),  -- #27

    -- One active reservation with a pending payment
    (25, '09901200006', NULL,
        CURRENT_DATE + TIME '19:00:00',
        CURRENT_DATE + TIME '19:15:00', 'Reserved')     -- #29
        ;


-- Insert Payments
    -- More than one payment attempt is included for some reservations.

INSERT INTO Payment
    (ReservationID, PaymentAmount, PaymentMethod,
     PaymentDatetime, PaymentStatus)
VALUES
    -- Successful historical payments
    (1,  90.000, 'Card', '2025-10-01 10:05:00', 'Success'),     -- #1
    (2, 150.000, 'Card', '2025-10-05 11:05:00', 'Success'),     -- #2
    (3, 100.000, 'Wallet', '2026-01-20 09:05:00', 'Success'),   -- #3
    (4,  75.000, 'Card', '2026-03-15 13:05:00', 'Success'),     -- #4
    (5,  30.000, 'Wallet', '2026-04-10 14:05:00', 'Success'),   -- #5
    (6,  30.000, 'Card', '2026-05-12 12:05:00', 'Success'),     -- #6
    (7,  25.000, 'Card', '2026-06-18 16:05:00', 'Success'),     -- #7

    -- Failed payments for cancelled reservations
    (8,  40.000, 'Card',
        CURRENT_DATE - 8 + TIME '09:05:00', 'Failed'),      -- #8

    (9,  70.000, 'Card',
        CURRENT_DATE - 7 + TIME '10:05:00', 'Failed'),      -- #9

    (12, 140.000, 'Card',
        CURRENT_DATE - 12 + TIME '08:35:00', 'Failed'),     -- #10

    (15, 45.000, 'Card',
        CURRENT_DATE - 9 + TIME '11:35:00', 'Failed'),      -- #11

    -- Recent successful purchases
    (16, 50.000, 'Card',
        CURRENT_DATE - 1 + TIME '10:05:00', 'Success'),     -- #12

    -- Reservation 17: failed attempt, then success
    (17, 40.000, 'Card',
        CURRENT_DATE - 5 + TIME '11:02:00', 'Failed'),      -- #13
    (17, 40.000, 'Wallet',
        CURRENT_DATE - 5 + TIME '11:05:00', 'Success'),     -- #14

    (18, 35.000, 'Card',
        CURRENT_DATE - 4 + TIME '12:05:00', 'Success'),     -- #15

    (19, 45.000, 'Card',
        CURRENT_DATE - 3 + TIME '13:05:00', 'Success'),     -- #16

    (20, 50.000, 'Wallet',
        CURRENT_DATE - 1 + TIME '11:05:00', 'Success'),     -- #17

    -- Reservation 21: failed attempt, then success
    (21, 70.000, 'Card',
        CURRENT_DATE - 4 + TIME '14:02:00', 'Failed'),      -- #18
    (21, 70.000, 'Wallet',
        CURRENT_DATE - 4 + TIME '14:05:00', 'Success'),     -- #19

    (22, 35.000, 'Card',
        CURRENT_DATE - 2 + TIME '10:35:00', 'Success'),     -- #20

    (23, 80.000, 'Card',
        CURRENT_DATE - 1 + TIME '12:05:00', 'Success'),     -- #21

    (24, 60.000, 'Wallet',
        CURRENT_DATE - 1 + TIME '15:05:00', 'Success'),     -- #22

    -- Reservation 25: failed attempt, then success
    (25, 130.000, 'Card',
        CURRENT_DATE + TIME '18:02:00', 'Failed'),          -- #23
    (25, 130.000, 'Wallet',
        CURRENT_DATE + TIME '18:04:00', 'Success'),         -- #24

    (26, 75.000, 'Card',
        CURRENT_DATE + TIME '09:05:00', 'Success'),         -- #25

    (27, 140.000, 'Card',
        CURRENT_DATE + TIME '13:05:00', 'Success'),         -- #26

    -- Active reservation
    (28, 100.000, 'Card',
        CURRENT_DATE + TIME '19:05:00', 'Pending')          -- #27
    ;


-- Insert Reports

    -- Ticket 5 has four reports through reservations 8 and 17.
    -- This makes it the ticket with the largest report count.

INSERT INTO Report
    (ReservationID, SubmitterPhoneNum,
     ReportCategory, ReportDescription, ReportStatus)
VALUES
    (8,  '09901200006', 'Payment Issue',
        'The payment failed but the bank temporarily blocked the amount.',  -- #1
        'Reviewed'),

    (8,  '09901200006', 'Payment Issue',
        'The failed payment message was not clear.',                        -- #2
        'Reviewed'),

    (17, '09901200001', 'Seat Issue',
        'The seat label was difficult to find.',                            -- #3
        'Reviewed'),

    (17, '09901200001', 'Entry Problem',
        'The entrance gate shown on the ticket was crowded.',               -- #4
        'Reviewed'),

    (21, '09901200002', 'Payment Issue',
        'The first payment attempt failed.',                                -- #5
        'Reviewed'),

    (6,  '09901200005', 'Payment Issue',
        'The payment confirmation arrived late.',                           -- #6
        'Reviewed'),

    (12, '09901200004', 'Seat Issue',
        'The selected seat was released after cancellation.',               -- #7
        'Reviewed'),

    (24, '09901200003', 'Wrong Information',
        'The event information page showed an old starting time.',          -- #8
        'Reviewed'),

    (25, '09901200007', 'Entry Problem',
        'The mobile ticket barcode took time to appear.',                   -- #9
        'Pending'),

    (11, '09901200006', 'Refund Issue',
        'The cancelled reservation refund took longer than expected.',      -- #10
        'Reviewed');


-- Insert Report Reviews
    -- Only reviewed reports are included here.

INSERT INTO ReportRev (ReportID, ReviewerPhoneNum)
VALUES
    (1,  '09901200111'),
    (2,  '09901200222'),
    (3,  '09901200111'),
    (4,  '09901200222'),
    (5,  '09901200111'),
    (6,  '09901200222'),
    (7,  '09901200333'),
    (8,  '09901200111'),
    (10, '09901200333');


-- queries

-- 1) Return the first name and last name of users who have never reserved any ticket 
SELECT FirstName, LastName 
FROM Users 
WHERE PhoneNumber NOT IN (SELECT ReservationPhoneNum FROM Reservation) AND UserRole = 'Spectator';

-- 2) Return users who bought at least one ticket
SELECT DISTINCT u.FirstName, u.LastName 
FROM Users u 
JOIN Reservation r ON u.PhoneNumber = r.ReservationPhoneNum
WHERE r.ReservationStatus = 'Paid';

-- 3) Return each user's total payments by month
SELECT r.ReservationPhoneNum, 
       EXTRACT(MONTH FROM p.PaymentDatetime) AS PaymentMonth, 
       SUM(p.PaymentAmount) AS TotalPaid
FROM Payment p
JOIN Reservation r ON p.ReservationID = r.ReservationID
WHERE p.PaymentStatus = 'Success'
GROUP BY r.ReservationPhoneNum, EXTRACT(MONTH FROM p.PaymentDatetime);

-- 4) Display the list of users who have purchased a ticket only once in each city
SELECT u.PhoneNumber, u.FirstName, u.LastName, v.VenueCity 
FROM Users u 
JOIN Reservation r ON u.PhoneNumber = r.ReservationPhoneNum 
JOIN Ticket t ON r.TicketID = t.TicketID 
JOIN Matches m ON t.MatchID = m.MatchID 
JOIN Venue v ON m.VenueID = v.VenueID 
WHERE r.ReservationStatus = 'Paid' 
GROUP BY u.PhoneNumber, u.FirstName, u.LastName, v.VenueCity 
HAVING COUNT(r.ReservationID) = 1;

-- 5) Return the information of the user who purchased the most recent ticket
SELECT u.*
FROM Users u
JOIN Reservation r ON u.PhoneNumber = r.ReservationPhoneNum
WHERE r.ReservationStatus = 'Paid'
ORDER BY r.ReservationDateTime DESC
LIMIT 1;

-- 6) Return the phone number and email address of users whose total payments are greater than the average total payment of all users
WITH UserTotals AS (
    SELECT r.ReservationPhoneNum, SUM(p.PaymentAmount) AS TotalSpend
    FROM Payment p
    JOIN Reservation r ON p.ReservationID = r.ReservationID
    WHERE p.PaymentStatus = 'Success'
    GROUP BY r.ReservationPhoneNum
)
SELECT u.PhoneNumber, u.Email 
FROM Users u
JOIN UserTotals ut ON u.PhoneNumber = ut.ReservationPhoneNum
WHERE ut.TotalSpend > (SELECT AVG(TotalSpend) FROM UserTotals);

-- 7) Display the number of sold tickets for each sport
SELECT m.SportType, COUNT(r.ReservationID) AS TicketsSold
FROM Matches m
JOIN Ticket t ON m.MatchID = t.MatchID
JOIN Reservation r ON t.TicketID = r.TicketID
WHERE r.ReservationStatus = 'Paid'
GROUP BY m.SportType;

-- 8) Return the top 3 users by ticket purchases in the last week
SELECT u.FirstName, u.LastName, COUNT(r.ReservationID) AS TotalPurchases
FROM Users u
JOIN Reservation r ON u.PhoneNumber = r.ReservationPhoneNum
WHERE r.ReservationStatus = 'Paid' 
  AND r.ReservationDateTime >= NOW() - INTERVAL '7 days'
GROUP BY u.PhoneNumber, u.FirstName, u.LastName
ORDER BY TotalPurchases DESC 
LIMIT 3;

-- 9) Display the number of tickets sold in Tehran province, grouped by city
SELECT v.VenueCity, COUNT(r.ReservationID) AS TicketsSold
FROM Venue v
JOIN Matches m ON v.VenueID = m.VenueID
JOIN Ticket t ON m.MatchID = t.MatchID
JOIN Reservation r ON t.TicketID = r.TicketID
WHERE r.ReservationStatus = 'Paid' 
  AND v.VenueCity IN ('Tehran', 'Rey', 'Varamin', 'Damavand', 'Shemroon', 'Pakdasht', 'Firuzkuh')
GROUP BY v.VenueCity;

-- 10) List cities where the oldest registered users has made a purchase
SELECT DISTINCT v.VenueCity 
FROM Venue v 
JOIN Matches m ON v.VenueID = m.VenueID 
JOIN Ticket t ON m.MatchID = t.MatchID 
JOIN Reservation r ON t.TicketID = r.TicketID 
WHERE r.ReservationStatus = 'Paid' 
  AND r.ReservationPhoneNum = (
      -- Subquery to find the single oldest user based on SignUpDate
      SELECT PhoneNumber 
      FROM Users 
      ORDER BY SignUpDate ASC 
      LIMIT 1
  );

-- 11) List the names of support staff
SELECT FirstName, LastName 
FROM Users 
WHERE UserRole = 'Support';

-- 12) Return the names of users who have purchased at least 2 tickets
SELECT u.FirstName, u.LastName
FROM Users u
JOIN Reservation r ON u.PhoneNumber = r.ReservationPhoneNum
WHERE r.ReservationStatus = 'Paid'
GROUP BY u.PhoneNumber, u.FirstName, u.LastName
HAVING COUNT(r.ReservationID) >= 2;

-- 13) List users who bought at most 2 tickets for a sport
SELECT DISTINCT u.FirstName, u.LastName
FROM Users u 
JOIN Reservation r ON u.PhoneNumber = r.ReservationPhoneNum 
JOIN Ticket t ON r.TicketID = t.TicketID 
JOIN Matches m ON t.MatchID = m.MatchID  
WHERE r.ReservationStatus = 'Paid' 
GROUP BY u.PhoneNumber, u.FirstName, u.LastName, m.SportType
HAVING COUNT(r.ReservationID) <= 2;

-- 14) Return users who bought tickets for all sport types
SELECT u.PhoneNumber, u.Email 
FROM Users u 
JOIN Reservation r ON u.PhoneNumber = r.ReservationPhoneNum 
JOIN Ticket t ON r.TicketID = t.TicketID 
JOIN Matches m ON t.MatchID = m.MatchID 
WHERE r.ReservationStatus = 'Paid' 
GROUP BY u.PhoneNumber, u.Email 
HAVING COUNT(DISTINCT m.SportType) = 3;

-- 15) List today's ticket purchases by purchase time
SELECT t.*, r.ReservationDateTime 
FROM Ticket t 
JOIN Reservation r ON t.TicketID = r.TicketID 
WHERE DATE(r.ReservationDateTime) = CURRENT_DATE 
  AND r.ReservationStatus = 'Paid' 
ORDER BY r.ReservationDateTime ASC;

-- 16) Show the second best-selling ticket
SELECT m.*, COUNT(r.ReservationID) AS TotalTicketsSold
FROM Matches m
JOIN Ticket t ON m.MatchID = t.MatchID
JOIN Reservation r ON t.TicketID = r.TicketID
WHERE r.ReservationStatus = 'Paid'
GROUP BY m.MatchID
ORDER BY TotalTicketsSold DESC
LIMIT 1 OFFSET 1;

-- 17) Return the name of the support staff member with the highest number of reservation cancellations, along with their cancellation percentage
WITH CancelStats AS (
    SELECT CancellationPhoneNum, 
           COUNT(ReservationID) AS CancelCount,
           (COUNT(ReservationID) * 100.0 / (SELECT COUNT(ReservationID) FROM Reservation WHERE ReservationStatus = 'Cancelled')) AS CancelPercentage
    FROM Reservation
    WHERE ReservationStatus = 'Cancelled'
      AND CancellationPhoneNum IS NOT NULL
    GROUP BY CancellationPhoneNum
)
SELECT u.FirstName, u.LastName, cs.CancelCount, cs.CancelPercentage
FROM Users u
JOIN CancelStats cs ON u.PhoneNumber = cs.CancellationPhoneNum
ORDER BY cs.CancelCount DESC
LIMIT 1;

-- 18) Update the last name of the user with the highest number of cancelled tickets to "Reddington"
UPDATE Users 
SET LastName = 'Reddington'
WHERE PhoneNumber = (
    SELECT ReservationPhoneNum 
    FROM Reservation 
    WHERE ReservationStatus = 'Cancelled' 
    GROUP BY ReservationPhoneNum 
    ORDER BY COUNT(ReservationID) DESC 
    LIMIT 1
);

-- 19) Delete all Reddington's all cancelled tickets
DELETE FROM Reservation 
WHERE ReservationStatus = 'Cancelled' 
  AND ReservationPhoneNum = (SELECT PhoneNumber FROM Users WHERE LastName = 'Reddington');

-- 20) Delete all cancelled tickets
DELETE FROM Reservation 
WHERE ReservationStatus = 'Cancelled';

-- 21) Reduce the price by 10% for tickets that were sold yesterday for mathces held at Azadi stadium
UPDATE Ticket 
SET TicketPrice = TicketPrice * 0.90
WHERE MatchID IN (
    SELECT m.MatchID 
    FROM Matches m
    JOIN Venue v ON m.VenueID = v.VenueID
    WHERE v.VenueName = 'Azadi Stadium' 
      AND DATE(m.MatchDatetime) = CURRENT_DATE - INTERVAL '1 day'
);

-- 22) Show the subject and report count for the most reported ticket
SELECT rep.ReportCategory, COUNT(rep.ReportID) AS ReportCount
FROM Report rep
JOIN Reservation r ON rep.ReservationID = r.ReservationID
WHERE r.TicketID = (
    SELECT sub_r.TicketID 
    FROM Reservation sub_r
    JOIN Report sub_rep ON sub_rep.ReservationID = sub_r.ReservationID
    GROUP BY sub_r.TicketID 
    ORDER BY COUNT(sub_rep.ReportID) DESC 
    LIMIT 1
)
GROUP BY rep.ReportCategory;


-- functions

-- 1) Receive a user’s email or phone number and show their purchased tickets ordered by purchase time.

CREATE OR REPLACE FUNCTION get_user_purchased_tickets(
    p_user_identifier TEXT
)
RETURNS TABLE (
    reservation_id     INT,
    ticket_id          INT,

    seat_number        VARCHAR(10),
    seat_row           VARCHAR(10),
    seat_section       VARCHAR(50),
    ticket_class       VARCHAR(50),
    ticket_price       NUMERIC(11, 3),

    match_id           INT,
    sport_type         VARCHAR(50),
    home_team          VARCHAR(100),
    away_team          VARCHAR(100),
    match_datetime     TIMESTAMP,
    league_name        VARCHAR(100),

    venue_name         VARCHAR(150),
    venue_city         VARCHAR(100),

    purchase_datetime  TIMESTAMP
)

AS $$

    WITH SelectedUser AS (
        SELECT u.PhoneNumber
        FROM Users AS u
        WHERE u.PhoneNumber = p_user_identifier
           OR LOWER(u.Email) = LOWER(p_user_identifier)
    ),
    SuccessfulPayments AS (
        SELECT
            p.ReservationID,
            MIN(p.PaymentDatetime) AS PurchaseDatetime
        FROM Payment AS p
        WHERE p.PaymentStatus = 'Success'
        GROUP BY p.ReservationID
    )
    SELECT
        r.ReservationID,
        t.TicketID,

        t.SeatNumber,
        t.SeatRow,
        t.SeatSection,
        t.TicketClass,
        t.TicketPrice,

        m.MatchID,
        m.SportType,
        m.HomeTeam,
        m.AwayTeam,
        m.MatchDatetime,
        m.LeagueName,

        v.VenueName,
        v.VenueCity,

        sp.PurchaseDatetime
    FROM Reservation AS r
    JOIN SelectedUser AS su
        ON su.PhoneNumber = r.ReservationPhoneNum
    JOIN SuccessfulPayments AS sp
        ON sp.ReservationID = r.ReservationID
    JOIN Ticket AS t
        ON t.TicketID = r.TicketID
    JOIN Matches AS m
        ON m.MatchID = t.MatchID
    JOIN Venue AS v
        ON v.VenueID = m.VenueID
    WHERE r.ReservationStatus = 'Paid'

    ORDER BY sp.PurchaseDatetime DESC;
$$
LANGUAGE SQL;


-- 2) Given a support staff member’s email or phone number, list users whose reservations were cancelled at least once.

CREATE OR REPLACE FUNCTION get_users_cancelled_by_support(
    p_support_identifier TEXT
)
RETURNS TABLE (
    customer_phone      VARCHAR(11),
    customer_first_name VARCHAR(50),
    customer_last_name  VARCHAR(50),
    customer_email      VARCHAR(255)
)

AS $$

    WITH SelectedSupport AS (
        SELECT u.PhoneNumber
        FROM Users AS u
        WHERE (
                u.PhoneNumber = p_support_identifier
                OR LOWER(u.Email) = LOWER(p_support_identifier)
              )
          AND u.UserRole = 'Support'
    )
    SELECT DISTINCT
        customer.PhoneNumber,
        customer.FirstName,
        customer.LastName,
        customer.Email
    FROM Reservation AS r
    JOIN SelectedSupport AS ss
        ON ss.PhoneNumber = r.CancellationPhoneNum
    JOIN Users AS customer
        ON customer.PhoneNumber = r.ReservationPhoneNum
    WHERE r.ReservationStatus = 'Cancelled';
$$
LANGUAGE SQL;


-- 3) Given a city name, list the tickets purchased in that city.

CREATE OR REPLACE FUNCTION get_purchased_tickets_by_city(
    p_city_name TEXT
)
RETURNS TABLE (
    reservation_id     INT,
    ticket_id          INT,
    buyer_phone        VARCHAR(11),
    buyer_first_name   VARCHAR(50),
    buyer_last_name    VARCHAR(50),
    ticket_class       VARCHAR(50),
    ticket_price       DECIMAL(11, 3),
    seat_number        VARCHAR(10),
    seat_row           VARCHAR(10),
    seat_section       VARCHAR(50),
    match_id           INT,
    home_team          VARCHAR(100),
    away_team          VARCHAR(100),
    match_datetime     TIMESTAMP,
    venue_name         VARCHAR(150)
)

AS $$

    SELECT
        r.ReservationID,
        t.TicketID,
        buyer.PhoneNumber,
        buyer.FirstName,
        buyer.LastName,
        t.TicketClass,
        t.TicketPrice,
        t.SeatNumber,
        t.SeatRow,
        t.SeatSection,
        m.MatchID,
        m.HomeTeam,
        m.AwayTeam,
        m.MatchDatetime,
        v.VenueName

    FROM Reservation AS r
    JOIN Users AS buyer
        ON buyer.PhoneNumber = r.ReservationPhoneNum
    JOIN Ticket AS t
        ON t.TicketID = r.TicketID
    JOIN Matches AS m
        ON m.MatchID = t.MatchID
    JOIN Venue AS v
        ON v.VenueID = m.VenueID
    WHERE r.ReservationStatus = 'Paid'
      AND LOWER(v.VenueCity) = LOWER(p_city_name)
$$
LANGUAGE SQL;


-- 4) Given a search term, return tickets where it appears in the spectator’s name, team names, venue, or ticket category.

CREATE OR REPLACE FUNCTION search_purchased_tickets(
    p_search_text TEXT
)
RETURNS TABLE (
    ticket_id       INT,
    seat_number     VARCHAR(10),
    seat_row        VARCHAR(10),
    seat_section    VARCHAR(50),
    ticket_class    VARCHAR(50),
    ticket_price    NUMERIC(11, 3),
    facilities      JSONB,

    sport_type      VARCHAR(50),
    home_team       VARCHAR(100),
    away_team       VARCHAR(100),
    match_datetime  TIMESTAMP,
    league_name     VARCHAR(100),

    venue_name      VARCHAR(150),
    venue_city      VARCHAR(100)
)
AS $$
    SELECT
        t.TicketID,
        t.SeatNumber,
        t.SeatRow,
        t.SeatSection,
        t.TicketClass,
        t.TicketPrice,
        t.Facilities,

        m.SportType,
        m.HomeTeam,
        m.AwayTeam,
        m.MatchDatetime,
        m.LeagueName,

        v.VenueName,
        v.VenueCity
    FROM Reservation AS r
    JOIN Users AS spectator
        ON spectator.PhoneNumber = r.ReservationPhoneNum
    JOIN Ticket AS t
        ON t.TicketID = r.TicketID
    JOIN Matches AS m
        ON m.MatchID = t.MatchID
    JOIN Venue AS v
        ON v.VenueID = m.VenueID
    WHERE r.ReservationStatus = 'Paid'

      AND (
          spectator.FirstName
              ILIKE '%' || TRIM(p_search_text) || '%'

          OR spectator.LastName
              ILIKE '%' || TRIM(p_search_text) || '%'

          OR CONCAT_WS(
                 ' ',
                 spectator.FirstName,
                 spectator.LastName
             ) ILIKE '%' || TRIM(p_search_text) || '%'

          OR m.HomeTeam
              ILIKE '%' || TRIM(p_search_text) || '%'

          OR m.AwayTeam
              ILIKE '%' || TRIM(p_search_text) || '%'

          OR v.VenueName
              ILIKE '%' || TRIM(p_search_text) || '%'

          OR t.TicketClass
              ILIKE '%' || TRIM(p_search_text) || '%'
      )
$$
LANGUAGE SQL;


-- 5) Given a user’s phone number or email, display other users who live in the same city.

CREATE OR REPLACE FUNCTION get_users_in_same_city(
    p_user_identifier TEXT
)
RETURNS TABLE (
    phone_number   VARCHAR(11),
    email          VARCHAR(255),
    first_name     VARCHAR(50),
    last_name      VARCHAR(50),
    residence_city VARCHAR(100)
)
AS $$
    WITH SelectedUser AS (
        SELECT
            u.PhoneNumber,
            u.ResidenceCity
        FROM Users AS u
        WHERE u.PhoneNumber = p_user_identifier
           OR LOWER(u.Email) = LOWER(TRIM(p_user_identifier))
    )
    SELECT
        other_user.PhoneNumber,
        other_user.Email,
        other_user.FirstName,
        other_user.LastName,
        other_user.ResidenceCity
    FROM Users AS other_user
    JOIN SelectedUser AS selected_user
        ON LOWER(other_user.ResidenceCity)
           = LOWER(selected_user.ResidenceCity)
    WHERE other_user.PhoneNumber <> selected_user.PhoneNumber
$$
LANGUAGE SQL;


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
    ORDER BY
        PurchaseCount DESC,
        u.LastName,
        u.FirstName
    LIMIT p_n;
$$
LANGUAGE SQL;


-- 7) Given a sport type, list its cancelled tickets ordered by match date.

CREATE FUNCTION get_cancelled_tickets_by_sport(
    p_sport_type TEXT
)
RETURNS TABLE (
    reservation_id INT,
    ticket_id       INT,
    seat_number     VARCHAR(10),
    seat_row        VARCHAR(10),
    seat_section    VARCHAR(50),
    ticket_class    VARCHAR(50),
    ticket_price    NUMERIC(11, 3),
    facilities      JSONB,
    home_team       VARCHAR(100),
    away_team       VARCHAR(100),
    match_datetime  TIMESTAMP,
    league_name     VARCHAR(100),
    venue_name      VARCHAR(150)
)
AS $$
    SELECT
        r.ReservationID,
        t.TicketID,
        t.SeatNumber,
        t.SeatRow,
        t.SeatSection,
        t.TicketClass,
        t.TicketPrice,
        t.Facilities,
        m.HomeTeam,
        m.AwayTeam,
        m.MatchDatetime,
        m.LeagueName,
        v.VenueName
    FROM Reservation AS r
    JOIN Ticket AS t
        ON t.TicketID = r.TicketID
    JOIN Matches AS m
        ON m.MatchID = t.MatchID
    JOIN Venue AS v
        ON v.VenueID = m.VenueID
    WHERE r.ReservationStatus = 'Cancelled'
      AND LOWER(m.SportType) = LOWER(TRIM(p_sport_type))
    ORDER BY m.MatchDatetime DESC;
$$
LANGUAGE SQL;


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