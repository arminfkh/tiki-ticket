from core.common.database import execute_returning, fetch_one

# authentication
GET_AUTH_USER_BY_EMAIL_SQL = """
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


def get_auth_user_by_email(
    email: str,
) -> dict | None:
    """
    Return one existing user by email for authentication flows.
    """
    return fetch_one(
        GET_AUTH_USER_BY_EMAIL_SQL,
        [email],
    )
