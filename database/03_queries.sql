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
SELECT u.FirstName, u.LastNamer
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