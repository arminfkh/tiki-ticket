from core.common.database import execute_returning, fetch_one

# sign up

CHECK_SIGNUP_CONFLICTS_SQL = """
    SELECT
        EXISTS (
            SELECT 1
            FROM Users
            WHERE PhoneNumber = %s
        ) AS phone_exists,

        EXISTS (
            SELECT 1
            FROM Users
            WHERE LOWER(Email) = LOWER(%s)
        ) AS email_exists;
"""


CREATE_USER_SQL = """
    INSERT INTO Users (
        PhoneNumber,
        Email,
        FirstName,
        LastName,
        ResidenceCity,
        HashedPassword,
        SignUpDate,
        AccountStatus,
        UserRole
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        CURRENT_TIMESTAMP,
        'Active',
        'Spectator'
    )
    RETURNING
        PhoneNumber AS phone_number,
        Email AS email,
        FirstName AS first_name,
        LastName AS last_name,
        ResidenceCity AS residence_city,
        SignUpDate AS signup_date,
        AccountStatus AS account_status,
        UserRole AS role;
"""


def get_signup_conflicts(
    phone_number: str,
    email: str,
):
    """
    Check whether the phone number or email already exists.
    """
    return fetch_one(CHECK_SIGNUP_CONFLICTS_SQL, [phone_number, email])


def create_user(
    *,
    phone_number: str,
    email: str,
    first_name: str,
    last_name: str,
    residence_city: str | None,
    hashed_password: str,
):
    """
    Insert a new spectator account and return its public data.
    """
    return execute_returning(
        CREATE_USER_SQL,
        [
            phone_number,
            email,
            first_name,
            last_name,
            residence_city,
            hashed_password,
        ],
    )


# password login

GET_USER_FOR_LOGIN_SQL = """
    SELECT
        PhoneNumber AS phone_number,
        Email AS email,
        FirstName AS first_name,
        LastName AS last_name,
        ResidenceCity AS residence_city,
        HashedPassword AS hashed_password,
        AccountStatus AS account_status,
        UserRole AS role
    FROM Users
    WHERE LOWER(Email) = LOWER(%s);
"""


def get_user_for_login(email: str) -> dict | None:
    """
    Find one user by email for password login.
    """
    return fetch_one(
        GET_USER_FOR_LOGIN_SQL,
        [email],
    )


# otp

GET_USER_FOR_OTP_SQL = """
    SELECT
        PhoneNumber AS phone_number,
        Email AS email,
        FirstName AS first_name,
        LastName AS last_name,
        ResidenceCity AS residence_city,
        AccountStatus AS account_status,
        UserRole AS role
    FROM Users
    WHERE PhoneNumber = %s;
"""


def get_user_for_otp(
    phone_number: str,
) -> dict | None:
    """
    Find one user by phone number for OTP login.
    """
    return fetch_one(
        GET_USER_FOR_OTP_SQL,
        [phone_number],
    )
