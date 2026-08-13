-- Insert Users

    -- Galileo and Nikola intentionally have no reservations.

INSERT INTO Users
    (PhoneNumber, Email, FirstName, LastName, ResidenceCity,
     HashedPassword, SignUpDate, AccountStatus, UserRole)
VALUES
    -- Supports
    -- Password: SupportPassword123!
    ('09901200111', 'alan.turing@example.com',       'Alan',    'Turing',      'London',   'pbkdf2_sha256$1000000$kzZ6YMY9jjetju52drc8VB$V8eBIbbAJ5Ac7me6hM41BEJwSYJEx074SDKq9GF8nuw=', '2024-03-10 09:15:00', 'Active',   'Support'),
    ('09901200222', 'grace.hopper@example.com',      'Grace',   'Hopper',      'London',   'pbkdf2_sha256$1000000$kzZ6YMY9jjetju52drc8VB$V8eBIbbAJ5Ac7me6hM41BEJwSYJEx074SDKq9GF8nuw=', '2024-08-14 10:45:00', 'Active',   'Support'),
    ('09901200333', 'abedii.mni@gmail.com',          'Mani',    'Abedi',       'London',   'pbkdf2_sha256$1000000$kzZ6YMY9jjetju52drc8VB$V8eBIbbAJ5Ac7me6hM41BEJwSYJEx074SDKq9GF8nuw=', '2024-04-12 11:30:00', 'Active',   'Support'),

    -- Spectators
    -- Password: TestPassword123!
    ('09901200001', 'arminfakhar2005@gmail.com',     'Armin',   'Fakhar',      'New York', 'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2024-05-18 14:20:00', 'Active',   'Spectator'),
    ('09901200002', 'linus.torvalds@example.com',    'Linus',   'Torvalds',    'Helsinki', 'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2024-05-18 14:20:00', 'Active',   'Spectator'),
    ('09901200003', 'tim.berners-lee@example.com',   'Tim',     'Berners-Lee', 'Helsinki', 'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2024-01-05 08:00:00', 'Active',   'Spectator'),
    ('09901200004', 'albert.einstein@example.com',   'Albert',  'Einstein',    'Warsaw',   'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2024-06-25 16:10:00', 'Active',   'Spectator'),
    ('09901200005', 'isaac.newton@example.com',      'Isaac',   'Newton',      'London',   'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2024-10-08 13:25:00', 'Active',   'Spectator'),
    ('09901200006', 'marie.curie@example.com',       'Marie',   'Curie',       'Warsaw',   'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2025-01-15 09:40:00', 'Active',   'Spectator'),
    ('09901200007', 'richard.feynman@example.com',   'Richard', 'Feynman',     'New York', 'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2025-03-22 12:05:00', 'Active',   'Spectator'),
    ('09901200008', 'louis.pasteur@example.com',     'Louis',   'Pasteur',     'Dole',     'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2025-05-19 15:35:00', 'Active',   'Spectator'),
    ('09901200009', 'galileo.galilei@example.com',   'Galileo', 'Galilei',     'Paris',    'pbkdf2_sha256$1000000$VjArQrUAdRmz7wGLWX63K1$LsrbI6/AUsgtluybtfzrkWp7L2rrO2CaYzYKFbjbHqA=',    '2025-07-07 17:20:00', 'Inactive', 'Spectator'),


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