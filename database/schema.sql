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
    VenueName VARCHAR(150) NOT NULL,
    Capacity INT CHECK (Capacity > 0)
);

CREATE TABLE Match (
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
    MatchID INT REFERENCES Match(MatchID) ON DELETE CASCADE,
    SeatNumber VARCHAR(10),
    SeatRow VARCHAR(10),
    SeatSection VARCHAR(50),
    TicketClass VARCHAR(50) CHECK (TicketClass IN ('Regular', 'Premium', 'VIP')) DEFAULT 'Regular',
    TicketPrice DECIMAL(11, 3) CHECK (TicketPrice >= 0),
    RemainedCapacity INT CHECK (RemainedCapacity >= 0),
    Facilities JSONB
);
