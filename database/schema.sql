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
    SubmitterPhoneNumber VARCHAR(11) REFERENCES Users(PhoneNumber) ON DELETE CASCADE,
    ReportCategory VARCHAR(100),
    ReportDescription TEXT,
    ReportStatus VARCHAR(20) CHECK (ReportStatus IN ('Pending', 'Reviewed'))
);

CREATE TABLE ReportRev (
    ReportID INT REFERENCES Report(ReportID) ON DELETE CASCADE,
    ReviewerPhoneNum VARCHAR(11) REFERENCES Users(PhoneNumber) ON DELETE CASCADE,
    PRIMARY KEY (ReportID, ReviewerPhoneNum)
);