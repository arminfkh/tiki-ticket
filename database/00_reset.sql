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