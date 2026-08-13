from core.common.database import execute_returning, fetch_one

# prevent duplicate signup
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


def get_signup_conflicts(
    phone_number: str,
    email: str,
):
    """
    Check whether the phone number or email already exists.
    {
    "phone_exists": True/False,
    "email_exists": True/False,
    }
    """
    return fetch_one(CHECK_SIGNUP_CONFLICTS_SQL, [phone_number, email])


# create user
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
