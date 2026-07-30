from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings


class InvalidAccessToken(Exception):
    """
    Raised when an access token is missing, invalid, or expired.
    """


def create_access_token(
    *,
    phone_number: str,
    role: str,
) -> str:
    """
    Create a signed JWT access token for one user.
    """
    issued_at = datetime.now(timezone.utc)

    expires_at = issued_at + timedelta(minutes=settings.JWT_ACCESS_TOKEN_MINUTES)

    payload = {
        "sub": phone_number,
        "role": role,
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """
    Validate and decode an access token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "role",
                    "type",
                    "iat",
                    "exp",
                ]
            },
        )
    except jwt.PyJWTError as exc:
        raise InvalidAccessToken("The access token is invalid or expired.") from exc

    if payload.get("type") != "access":
        raise InvalidAccessToken("The token is not an access token.")

    return payload
