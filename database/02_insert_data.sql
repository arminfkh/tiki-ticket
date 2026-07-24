-- Insert Users

INSERT INTO Users (PhoneNumber, Email, FirstName, LastName, ResidenceCity, HashedPassword, SignUpDate, AccountStatus, UserRole)
VALUES
    ('09901200111', 'alan.turing@example.com', 'Alan', 'Turing', 'London', 'hashed_password_support_01', '2024-03-10 09:15:00', 'Active', 'Support'),
    ('09901200222', 'grace.hopper@example.com', 'Grace', 'Hopper', 'London', 'hashed_password_support_02', '2024-08-14 10:45:00', 'Active', 'Support'),
    ('09901200333', 'ada.lovelace@example.com', 'Ada', 'Lovelace', 'London', 'hashed_password_support_03', '2024-04-12 11:30:00', 'Active', 'Support'),
    ('09901200001', 'linus.torvalds@example.com', 'Linus', 'Torvalds', 'Helsinki', 'hashed_password_user_01', '2024-05-18 14:20:00', 'Active', 'Spectator'),
    ('09901200002', 'tim.berners-lee@example.com', 'Tim', 'Berners-Lee', 'Helsinki', 'hashed_password_user_02', '2024-01-05 08:00:00', 'Active', 'Spectator'),
    ('09901200003', 'albert.einstein@example.com', 'Albert', 'Einstein', 'Warsaw', 'hashed_password_user_03', '2024-06-25 16:10:00', 'Active', 'Spectator'),
    ('09901200004', 'isaac.newton@example.com', 'Isaac', 'Newton', 'London', 'hashed_password_user_04', '2024-10-08 13:25:00', 'Active', 'Spectator'),
    ('09901200005', 'marie.curie@example.com', 'Marie', 'Curie', 'Warsaw', 'hashed_password_user_05', '2025-01-15 09:40:00', 'Active', 'Spectator'),
    ('09901200006', 'richard.feynman@example.com', 'Richard', 'Feynman', 'New York', 'hashed_password_user_06', '2025-03-22 12:05:00', 'Active', 'Spectator'),
    ('09901200007', 'louis.pasteur@example.com', 'Louis', 'Pasteur', 'Dole', 'hashed_password_user_07', '2025-05-19 15:35:00', 'Active', 'Spectator'),
    ('09901200008', 'galileo.galilei@example.com', 'Galileo', 'Galilei', 'Paris', 'hashed_password_user_08', '2025-07-07 17:20:00', 'Inactive', 'Spectator'),
    ('09901200009', 'nikola.tesla@example.com', 'Nikola', 'Tesla', 'New York', 'hashed_password_user_09', '2025-09-11 11:55:00', 'Active', 'Spectator');


-- Insert Venues

INSERT INTO Venue (VenueCity, VenueName, Capacity)
VALUES
    ('Tehran', 'Azadi Stadium', 80000),
    ('Tehran', 'Shahid Dastgerdi Stadium', 8250),
    ('Shemroon', 'Shemroon Boys Stadium', 4400),
    ('Damavand', 'Damavand Arena', 10000),
    ('London', 'Wembley Stadium', 90000),
    ('Barcelona', 'Camp Nou', 60000),
    ('Madrid', 'Santiago Bernabeu Stadium', 80000),
    ('Munich', 'Allianz Arena', 75000),
    ('New York', 'Rucker Park', 20000),
    ('Rio de Janeiro', 'Copacabana Beach', 10000);


-- Insert Matches

INSERT INTO Matches (VenueID, SportType, HomeTeam, AwayTeam, MatchDatetime, LeagueName)
VALUES
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Azadi Stadium'), 'Football', 'Esteghlal', 'Persepolis', (CURRENT_DATE + 10) + TIME '18:00:00', 'Persian Gulf Pro League'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Shahid Dastgerdi Stadium'), 'Volleyball', 'Paykan VC', 'Saipa VC', (CURRENT_DATE + 7) + TIME '16:30:00', 'Iran Volleyball Super League'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Shemroon Boys Stadium'), 'Basketball', 'Shemroon Wolves', 'Tehran Lions', (CURRENT_DATE + 12) + TIME '19:00:00', 'Iran Basketball League'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Damavand Arena'), 'Volleyball', 'Damavand Eagles', 'Karaj Stars', (CURRENT_DATE + 15) + TIME '17:30:00', 'National Volleyball League'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Wembley Stadium'), 'Football', 'England', 'Germany', (CURRENT_DATE + 20) + TIME '20:00:00', 'International Friendly'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Camp Nou'), 'Football', 'Barcelona', 'Valencia', (CURRENT_DATE + 25) + TIME '21:00:00', 'La Liga'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Santiago Bernabeu Stadium'), 'Football', 'Real Madrid', 'Atletico Madrid', (CURRENT_DATE + 30) + TIME '21:00:00', 'La Liga'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Alianz Arena'), 'Basketball', 'Bayern Baskets', 'Berlin Bears', (CURRENT_DATE + 35) + TIME '20:30:00', 'German Basketball League'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Rucker Park'), 'Basketball', 'New York Ballers', 'Brooklyn Kings', (CURRENT_DATE + 18) + TIME '19:30:00', 'New York Basketball League'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Copacabana Beach'), 'Volleyball', 'Rio Spikers', 'Sao Paulo Volley', (CURRENT_DATE + 22) + TIME '18:00:00', 'Brazil Volleyball Championship'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Azadi Stadium'), 'Basketball', 'Tehran Tigers', 'Isfahan Warriors', (CURRENT_DATE + 14) + TIME '19:00:00', 'Iran Basketball Super League'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Wembley Stadium'), 'Volleyball', 'London Lions VC', 'Paris Volley', (CURRENT_DATE + 28) + TIME '18:45:00', 'International Volleyball Cup'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Camp Nou'), 'Basketball', 'Barcelona Giants', 'Madrid Hoops', (CURRENT_DATE + 32) + TIME '19:30:00', 'Spanish Basketball League'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Rucker Park'), 'Volleyball', 'Manhattan VC', 'Queens VC', (CURRENT_DATE + 40) + TIME '17:00:00', 'New York Volleyball Cup'),
    ((SELECT VenueID FROM Venue WHERE VenueName = 'Copacabana Beach'), 'Football', 'Rio United', 'Santos FC', (CURRENT_DATE + 45) + TIME '20:00:00', 'Brazil Football Cup');


-- Insert Tickets

INSERT INTO Ticket (MatchID, SeatNumber, SeatRow, SeatSection, TicketClass, TicketPrice, RemainedCapacity, Facilities)
VALUES
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Esteghlal' AND AwayTeam = 'Persepolis'), '101', 'A', 'East Stand', 'Regular', 40.000, 5000, '{"parking": true, "snack": false}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Esteghlal' AND AwayTeam = 'Persepolis'), '201', 'B', 'West Stand', 'Premium', 80.000, 2500, '{"parking": true, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Esteghlal' AND AwayTeam = 'Persepolis'), '1', 'VIP', 'VIP Box', 'VIP', 150.000, 500, '{"parking": true, "snack": true, "lounge": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Paykan VC' AND AwayTeam = 'Saipa VC'), '15', 'C', 'North Stand', 'Regular', 25.000, 1200, '{"parking": false, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Paykan VC' AND AwayTeam = 'Saipa VC'), '16', 'C', 'Central Stand', 'Premium', 45.000, 600, '{"parking": true, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Shemroon Wolves' AND AwayTeam = 'Tehran Lions'), '25', 'D', 'Lower Level', 'Regular', 30.000, 1000, '{"snack": true, "wheelchair_access": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Damavand Eagles' AND AwayTeam = 'Karaj Stars'), '40', 'E', 'South Stand', 'Regular', 20.000, 900, '{"parking": true, "snack": false}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'England' AND AwayTeam = 'Germany'), '110', 'F', 'Standard Area', 'Regular', 120.000, 10000, '{"parking": false, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'England' AND AwayTeam = 'Germany'), '111', 'F', 'Club Area', 'Premium', 250.000, 3000, '{"parking": true, "snack": true, "lounge": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Barcelona' AND AwayTeam = 'Valencia'), '45', 'G', 'North Stand', 'Regular', 110.000, 6000, '{"parking": true, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Barcelona' AND AwayTeam = 'Valencia'), '5', 'VIP', 'VIP Box', 'VIP', 300.000, 700, '{"parking": true, "snack": true, "lounge": true, "meal": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Real Madrid' AND AwayTeam = 'Atletico Madrid'), '10', 'H', 'Central Stand', 'Premium', 220.000, 2500, '{"parking": true, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Bayern Baskets' AND AwayTeam = 'Berlin Bears'), '22', 'J', 'Lower Level', 'Regular', 70.000, 1800, '{"parking": true, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'New York Ballers' AND AwayTeam = 'Brooklyn Kings'), '1', 'K', 'Courtside', 'Premium', 350.000, 300, '{"parking": true, "snack": true, "meal": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'New York Ballers' AND AwayTeam = 'Brooklyn Kings'), '50', 'L', 'Upper Level', 'Regular', 90.000, 1500, '{"parking": false, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Rio Spikers' AND AwayTeam = 'Sao Paulo Volley'), '12', 'M', 'Beachside Area', 'Regular', 60.000, 800, '{"snack": true, "sea_view": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Tehran Tigers' AND AwayTeam = 'Isfahan Warriors'), '18', 'N', 'Central Stand', 'Premium', 75.000, 1100, '{"parking": true, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'London Lions VC' AND AwayTeam = 'Paris Volley'), '30', 'P', 'North Stand', 'Regular', 85.000, 1700, '{"parking": false, "snack": true, "wheelchair_access": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Barcelona Giants' AND AwayTeam = 'Madrid Hoops'), '7', 'Q', 'Courtside', 'VIP', 280.000, 400, '{"parking": true, "snack": true, "lounge": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Manhattan VC' AND AwayTeam = 'Queens VC'), '26', 'R', 'East Stand', 'Regular', 65.000, 1300, '{"parking": false, "snack": true}'),
    ((SELECT MatchID FROM Matches WHERE HomeTeam = 'Rio United' AND AwayTeam = 'Santos FC'), '33', 'S', 'Beach Stand', 'Premium', 140.000, 900, '{"snack": true, "sea_view": true, "lounge": true}');


-- Insert Reservations

-- This creates:
-- 32 paid reservations
-- 7 cancelled reservations
-- 2 currently reserved reservations
-- Galileo Galilei and Nikola Tesla with no reservations
-- Linus Torvalds, Tim Berners-Lee, and Albert Einstein as the top three recent buyers
-- Tim Berners-Lee purchasing football, volleyball, and basketball tickets
-- Marie Curie with the most cancellations
-- Alan Turing as the support user who performs the most cancellations
-- Wembley Regular as the best-selling ticket
-- Azadi Premium as the second-best-selling ticket

INSERT INTO Reservation (TicketID, ReservationPhoneNum, CancellationPhoneNum, ReservationDateTime, ReservationExpireDatetime, ReservationStatus)
VALUES
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Regular'), '09901200001', NULL, CURRENT_DATE + TIME '09:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Regular'), '09901200001', NULL, CURRENT_DATE + TIME '09:30:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Regular'), '09901200002', NULL, CURRENT_DATE + TIME '10:15:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Regular'), '09901200003', NULL, (CURRENT_DATE - 2) + TIME '18:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Regular'), '09901200004', NULL, (CURRENT_DATE - 4) + TIME '16:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Regular'), '09901200005', NULL, (CURRENT_DATE - 6) + TIME '15:30:00', NULL, 'Paid'),

    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Premium'), '09901200002', NULL, (CURRENT_DATE - 1) + TIME '12:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Premium'), '09901200001', NULL, (CURRENT_DATE - 1) + TIME '13:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Premium'), '09901200003', NULL, (CURRENT_DATE - 1) + TIME '14:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Premium'), '09901200004', NULL, (CURRENT_DATE - 1) + TIME '15:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Premium'), '09901200005', NULL, (CURRENT_DATE - 1) + TIME '16:00:00', NULL, 'Paid'),

    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Regular'), '09901200002', NULL, (CURRENT_DATE - 1) + TIME '16:30:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Regular'), '09901200001', NULL, (CURRENT_DATE - 1) + TIME '17:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Regular'), '09901200006', NULL, (CURRENT_DATE - 1) + TIME '17:15:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Regular'), '09901200007', NULL, (CURRENT_DATE - 1) + TIME '17:30:00', NULL, 'Paid'),

    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Paykan VC' AND m.AwayTeam = 'Saipa VC' AND t.TicketClass = 'Regular'), '09901200002', NULL, CURRENT_DATE + TIME '12:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Shemroon Wolves' AND m.AwayTeam = 'Tehran Lions'), '09901200002', NULL, CURRENT_DATE + TIME '13:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Bayern Baskets' AND m.AwayTeam = 'Berlin Bears'), '09901200001', NULL, (CURRENT_DATE - 3) + TIME '19:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Rio Spikers' AND m.AwayTeam = 'Sao Paulo Volley'), '09901200003', NULL, (CURRENT_DATE - 5) + TIME '17:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium'), '09901200004', NULL, (CURRENT_DATE - 2) + TIME '20:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'London Lions VC' AND m.AwayTeam = 'Paris Volley'), '09901200005', NULL, (CURRENT_DATE - 6) + TIME '18:00:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Barcelona' AND m.AwayTeam = 'Valencia' AND t.TicketClass = 'Regular'), '09901200006', NULL, (CURRENT_DATE - 3) + TIME '20:30:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Damavand Eagles' AND m.AwayTeam = 'Karaj Stars'), '09901200007', NULL, (CURRENT_DATE - 4) + TIME '17:30:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'London Lions VC' AND m.AwayTeam = 'Paris Volley'), '09901200001', NULL, (CURRENT_DATE - 2) + TIME '14:30:00', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Barcelona' AND m.AwayTeam = 'Valencia' AND t.TicketClass = 'Regular'), '09901200003', NULL, (CURRENT_DATE - 3) + TIME '16:30:00', NULL, 'Paid'),

    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Barcelona' AND m.AwayTeam = 'Valencia' AND t.TicketClass = 'VIP'), '09901200002', NULL, date_trunc('month', CURRENT_DATE) - INTERVAL '2 months' + INTERVAL '5 days 12 hours', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium'), '09901200001', NULL, date_trunc('month', CURRENT_DATE) - INTERVAL '1 month' + INTERVAL '7 days 15 hours', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Barcelona Giants' AND m.AwayTeam = 'Madrid Hoops'), '09901200003', NULL, date_trunc('month', CURRENT_DATE) - INTERVAL '3 months' + INTERVAL '10 days 20 hours', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Tehran Tigers' AND m.AwayTeam = 'Isfahan Warriors'), '09901200004', NULL, date_trunc('month', CURRENT_DATE) - INTERVAL '2 months' + INTERVAL '15 days 19 hours', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Manhattan VC' AND m.AwayTeam = 'Queens VC'), '09901200005', NULL, date_trunc('month', CURRENT_DATE) - INTERVAL '1 month' + INTERVAL '12 days 18 hours', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Rio United' AND m.AwayTeam = 'Santos FC'), '09901200006', NULL, date_trunc('month', CURRENT_DATE) - INTERVAL '4 months' + INTERVAL '8 days 17 hours', NULL, 'Paid'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Real Madrid' AND m.AwayTeam = 'Atletico Madrid'), '09901200007', NULL, date_trunc('month', CURRENT_DATE) - INTERVAL '2 months' + INTERVAL '20 days 21 hours', NULL, 'Paid'),

    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Premium'), '09901200005', '09901200111', (CURRENT_DATE - 20) + TIME '10:00:00', NULL, 'Cancelled'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Rio Spikers' AND m.AwayTeam = 'Sao Paulo Volley'), '09901200005', '09901200111', (CURRENT_DATE - 15) + TIME '11:00:00', NULL, 'Cancelled'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium'), '09901200005', '09901200222', (CURRENT_DATE - 8) + TIME '12:00:00', NULL, 'Cancelled'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Damavand Eagles' AND m.AwayTeam = 'Karaj Stars'), '09901200003', '09901200111', (CURRENT_DATE - 12) + TIME '13:00:00', NULL, 'Cancelled'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Paykan VC' AND m.AwayTeam = 'Saipa VC' AND t.TicketClass = 'Premium'), '09901200003', '09901200333', (CURRENT_DATE - 7) + TIME '14:00:00', NULL, 'Cancelled'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Barcelona' AND m.AwayTeam = 'Valencia' AND t.TicketClass = 'Regular'), '09901200004', '09901200222', (CURRENT_DATE - 5) + TIME '15:00:00', NULL, 'Cancelled'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'VIP'), '09901200006', '09901200111', (CURRENT_DATE - 2) + TIME '16:00:00', NULL, 'Cancelled'),

    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Premium'), '09901200006', NULL, CURRENT_DATE + TIME '18:00:00', (CURRENT_DATE) + TIME '19:00:00', 'Reserved'),
    ((SELECT t.TicketID FROM Ticket t JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Barcelona' AND m.AwayTeam = 'Valencia' AND t.TicketClass = 'Regular'), '09901200007', NULL, CURRENT_DATE + TIME '19:00:00', (CURRENT_DATE) + TIME '20:00:00', 'Reserved');


-- Insert Payments

INSERT INTO Payment (ReservationID, PaymentAmount, PaymentMethod, PaymentDatetime, PaymentStatus)
VALUES
    (1, 120.000, 'Credit Card', CURRENT_TIMESTAMP - INTERVAL '10 minutes', 'Failed'),
    (1, 120.000, 'Bank Transfer', CURRENT_TIMESTAMP - INTERVAL '5 minutes', 'Success'),
    (2, 80.000, 'Credit Card', CURRENT_TIMESTAMP - INTERVAL '8 minutes', 'Failed'),
    (2, 80.000, 'Online Wallet', CURRENT_TIMESTAMP - INTERVAL '3 minutes', 'Success'),
    (3, 40.000, 'Credit Card', CURRENT_TIMESTAMP - INTERVAL '4 minutes', 'Pending');


-- Insert Reports

INSERT INTO Report (ReservationID, SubmitterPhoneNum, ReportCategory, ReportDescription, ReportStatus)
VALUES
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200004' LIMIT 1), '09901200004', 'Seat Issue', 'The courtside seat number was difficult to locate.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200001' LIMIT 1), '09901200001', 'Seat Issue', 'The assigned courtside seat was already occupied.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200005' LIMIT 1), '09901200005', 'Seat Issue', 'The seat information did not match the venue map.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200001' LIMIT 1), '09901200001', 'Payment Issue', 'The first payment attempt failed without an explanation.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200005' LIMIT 1), '09901200005', 'Payment Issue', 'The payment was deducted before the reservation was cancelled.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200004' LIMIT 1), '09901200004', 'Venue Facilities', 'The advertised meal facility was unavailable.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200005' LIMIT 1), '09901200005', 'Ticket Validation', 'The digital ticket could not be validated at the entrance.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200001' LIMIT 1), '09901200001', 'Seat Issue', 'The view from the assigned seat was partially blocked.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'New York Ballers' AND m.AwayTeam = 'Brooklyn Kings' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200005' LIMIT 1), '09901200005', 'Payment Issue', 'The refund was not immediately visible after cancellation.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200002' LIMIT 1), '09901200002', 'Payment Issue', 'The successful payment confirmation arrived late.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Esteghlal' AND m.AwayTeam = 'Persepolis' AND t.TicketClass = 'Premium' AND r.ReservationPhoneNum = '09901200003' LIMIT 1), '09901200003', 'Payment Issue', 'The payment page showed an incorrect temporary status.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'England' AND m.AwayTeam = 'Germany' AND t.TicketClass = 'Regular' AND r.ReservationPhoneNum = '09901200005' LIMIT 1), '09901200005', 'Access Issue', 'The entrance gate printed on the ticket was closed.', 'Reviewed'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'London Lions VC' AND m.AwayTeam = 'Paris Volley' AND r.ReservationPhoneNum = '09901200001' LIMIT 1), '09901200001', 'Venue Facilities', 'Wheelchair access signs were not clear.', 'Pending'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Barcelona' AND m.AwayTeam = 'Valencia' AND t.TicketClass = 'Regular' AND r.ReservationPhoneNum = '09901200006' LIMIT 1), '09901200006', 'Ticket Validation', 'The QR code required several scans before validation.', 'Pending'),
    ((SELECT r.ReservationID FROM Reservation r JOIN Ticket t ON t.TicketID = r.TicketID JOIN Matches m ON m.MatchID = t.MatchID WHERE m.HomeTeam = 'Damavand Eagles' AND m.AwayTeam = 'Karaj Stars' AND r.ReservationPhoneNum = '09901200007' LIMIT 1), '09901200007', 'Seat Issue', 'The seat row label was missing inside the venue.', 'Pending');


-- Insert Report Reviewers

-- Insert Report Reviewers

INSERT INTO ReportRev (ReportID, ReviewerPhoneNum)
VALUES
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The courtside seat number was difficult to locate.'), '09901200111'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The assigned courtside seat was already occupied.'), '09901200111'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The assigned courtside seat was already occupied.'), '09901200222'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The seat information did not match the venue map.'), '09901200222'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The first payment attempt failed without an explanation.'), '09901200111'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The first payment attempt failed without an explanation.'), '09901200333'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The payment was deducted before the reservation was cancelled.'), '09901200333'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The advertised meal facility was unavailable.'), '09901200222'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The digital ticket could not be validated at the entrance.'), '09901200111'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The view from the assigned seat was partially blocked.'), '09901200222'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The refund was not immediately visible after cancellation.'), '09901200111'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The refund was not immediately visible after cancellation.'), '09901200333'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The successful payment confirmation arrived late.'), '09901200333'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The payment page showed an incorrect temporary status.'), '09901200222'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The entrance gate printed on the ticket was closed.'), '09901200111'),
    ((SELECT ReportID FROM Report WHERE ReportDescription = 'The entrance gate printed on the ticket was closed.'), '09901200222');