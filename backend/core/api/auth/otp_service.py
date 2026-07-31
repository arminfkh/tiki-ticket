import secrets

from django.conf import settings
from django.contrib.auth.hashers import (
    check_password,
    make_password,
)
from redis.exceptions import RedisError

from core.common.redis_client import redis_client


class OTPError(Exception):
    """
    Base exception for expected OTP errors.
    """


class OTPCooldownError(OTPError):
    """
    Raised when another OTP is requested too soon.
    """

    def __init__(self, retry_after: int):
        super().__init__("Please wait before requesting another OTP.")
        self.retry_after = retry_after


class InvalidOTPError(OTPError):
    """
    Raised when the OTP is incorrect or expired.
    """


class TooManyOTPAttemptsError(OTPError):
    """
    Raised after too many incorrect verification attempts.
    """


class OTPServiceUnavailableError(OTPError):
    """
    Raised when Redis cannot be reached.
    """


def _otp_key(phone_number: str) -> str:
    return f"auth:otp:{phone_number}"


def _attempts_key(phone_number: str) -> str:
    return f"auth:otp:attempts:{phone_number}"


def _cooldown_key(phone_number: str) -> str:
    return f"auth:otp:cooldown:{phone_number}"


def generate_and_store_otp(phone_number: str) -> str:
    """
    Generate an OTP and store its hash in Redis.

    Return the plain OTP so it can be delivered to the user.
    """
    otp_key = _otp_key(phone_number)
    attempts_key = _attempts_key(phone_number)
    cooldown_key = _cooldown_key(phone_number)

    try:
        cooldown_created = redis_client.set(
            cooldown_key,
            "1",
            ex=settings.OTP_RESEND_COOLDOWN_SECONDS,
            nx=True,
        )

        if not cooldown_created:
            retry_after = redis_client.ttl(cooldown_key)

            raise OTPCooldownError(retry_after=max(retry_after, 1))

        maximum_value = 10**settings.OTP_LENGTH

        otp = str(secrets.randbelow(maximum_value)).zfill(settings.OTP_LENGTH)

        hashed_otp = make_password(otp)

        pipeline = redis_client.pipeline()

        pipeline.setex(
            otp_key,
            settings.OTP_TTL_SECONDS,
            hashed_otp,
        )
        pipeline.delete(attempts_key)

        pipeline.execute()

        return otp

    except OTPCooldownError:
        raise

    except RedisError as exc:
        raise OTPServiceUnavailableError(
            "The OTP service is temporarily unavailable."
        ) from exc


def verify_otp_code(
    phone_number: str,
    submitted_otp: str,
) -> None:
    """
    Verify one submitted OTP.

    Delete the OTP after successful verification so it cannot be reused.
    """
    otp_key = _otp_key(phone_number)
    attempts_key = _attempts_key(phone_number)
    cooldown_key = _cooldown_key(phone_number)

    try:
        hashed_otp = redis_client.get(otp_key)

        if hashed_otp is None:
            raise InvalidOTPError("The OTP is invalid or has expired.")

        attempts = int(redis_client.get(attempts_key) or 0)

        if attempts >= settings.OTP_MAX_ATTEMPTS:
            redis_client.delete(
                otp_key,
                attempts_key,
            )

            raise TooManyOTPAttemptsError("Too many incorrect OTP attempts.")

        if not check_password(
            submitted_otp,
            hashed_otp,
        ):
            attempts = redis_client.incr(attempts_key)

            remaining_ttl = redis_client.ttl(otp_key)

            if remaining_ttl > 0:
                redis_client.expire(
                    attempts_key,
                    remaining_ttl,
                )

            if attempts >= settings.OTP_MAX_ATTEMPTS:
                redis_client.delete(
                    otp_key,
                    attempts_key,
                )

                raise TooManyOTPAttemptsError("Too many incorrect OTP attempts.")

            raise InvalidOTPError("The OTP is invalid or has expired.")

        redis_client.delete(
            otp_key,
            attempts_key,
            cooldown_key,
        )

    except (
        InvalidOTPError,
        TooManyOTPAttemptsError,
    ):
        raise

    except RedisError as exc:
        raise OTPServiceUnavailableError(
            "The OTP service is temporarily unavailable."
        ) from exc
