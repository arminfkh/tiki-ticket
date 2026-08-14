from core.common.database import (
    execute_returning,
    fetch_one,
)

GET_PROFILE_SQL = """
    SELECT
        PhoneNumber AS phone_number,
        Email AS email,
        FirstName AS first_name,
        LastName AS last_name,
        ResidenceCity AS residence_city,
        SignUpDate AS signup_date,
        AccountStatus AS account_status,
        UserRole AS role,
        WalletBalance AS wallet_balance
    FROM Users
    WHERE PhoneNumber = %s;
"""


def get_profile(
    phone_number: str,
) -> dict | None:
    """
    Find one user profile, including wallet balance.
    """
    return fetch_one(
        GET_PROFILE_SQL,
        [phone_number],
    )


def update_profile(
    *,
    phone_number: str,
    changes: dict,
) -> dict | None:
    """
    Update only the profile fields supplied by the user.

    WalletBalance is intentionally not updateable through
    the profile API. Wallet mutations must happen through
    payment/refund business logic.
    """
    column_map = {
        "email": "Email",
        "first_name": "FirstName",
        "last_name": "LastName",
        "residence_city": "ResidenceCity",
    }

    assignments = []
    params = []

    for (
        field_name,
        value,
    ) in changes.items():
        column_name = column_map[field_name]

        assignments.append(f"{column_name} = %s")

        params.append(value)

    params.append(phone_number)

    query = f"""
        UPDATE Users
        SET {", ".join(assignments)}
        WHERE PhoneNumber = %s
        RETURNING
            PhoneNumber AS phone_number,
            Email AS email,
            FirstName AS first_name,
            LastName AS last_name,
            ResidenceCity AS residence_city,
            SignUpDate AS signup_date,
            AccountStatus AS account_status,
            UserRole AS role,
            WalletBalance AS wallet_balance;
    """

    return execute_returning(
        query,
        params,
    )
