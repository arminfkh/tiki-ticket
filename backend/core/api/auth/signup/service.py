import json

from django.conf import settings
from redis.exceptions import RedisError

from core.common.redis_client import redis_client


class SignupServiceError(Exception):
    """
    Base exception for expected pending-signup errors.
    """


class PendingSignupNotFoundError(SignupServiceError):
    """
    Raised when pending signup data is missing or expired.
    """


class SignupServiceUnavailableError(SignupServiceError):
    """
    Raised when Redis cannot be reached.
    """


def _pending_signup_key(email: str) -> str:
    """
    auth:signup:pending:mani@example.com
    → user registration information

    auth:otp:signup:mani@example.com
    → hashed OTP
    """
    return f"auth:signup:pending:{email}"


def store_pending_signup(
    *,
    phone_number: str,
    email: str,
    first_name: str,
    last_name: str,
    residence_city: str | None,
    hashed_password: str,
) -> None:

    email = email.strip().lower()

    pending_user = {
        "phone_number": phone_number,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "residence_city": residence_city,
        "hashed_password": hashed_password,
    }

    serialized_user = json.dumps(pending_user)  # turn to json
    key = _pending_signup_key(email)

    try:
        redis_client.setex(
            key,
            settings.PENDING_SIGNUP_TTL_SECONDS,
            serialized_user,
        )

    except RedisError as exc:
        raise SignupServiceUnavailableError(
            "The signup service is temporarily unavailable."
        ) from exc


def get_pending_signup(email: str) -> dict:
    email = email.strip().lower()
    key = _pending_signup_key(email)

    try:
        serialized_user = redis_client.get(key)

    except RedisError as exc:
        raise SignupServiceUnavailableError(
            "The signup service is temporarily unavailable."
        ) from exc

    if serialized_user is None:
        raise PendingSignupNotFoundError(
            "The pending signup does not exist or has expired."
        )

    try:
        return json.loads(serialized_user)

    except json.JSONDecodeError as exc:
        raise SignupServiceUnavailableError(
            "The pending signup data is invalid."
        ) from exc


def delete_pending_signup(email: str) -> None:
    """
    delete after successful signup
    """
    email = email.strip().lower()
    key = _pending_signup_key(email)

    try:
        redis_client.delete(key)

    except RedisError as exc:
        raise SignupServiceUnavailableError(
            "The signup service is temporarily unavailable."
        ) from exc
