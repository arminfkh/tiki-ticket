import logging

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.common.authentication import create_access_token

from ..common import (
    error_response,
    get_required_text,
    read_json_object,
)

from .queries import get_auth_user_by_email

from ..otp_service import (
    InvalidOTPError,
    OTPCooldownError,
    OTPServiceUnavailableError,
    OTP_PURPOSE_LOGIN,
    TooManyOTPAttemptsError,
    delete_otp,
    generate_and_store_otp,
    verify_otp_code,
)

from ..email_service import (
    EmailDeliveryError,
    send_otp_email,
)

logger = logging.getLogger(__name__)


def _build_public_user(user: dict) -> dict:
    """
    Return user fields that are safe to expose in API responses.
    """
    return {
        "phone_number": user["phone_number"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "residence_city": user["residence_city"],
        "account_status": user["account_status"],
        "role": user["role"],
    }


@csrf_exempt
@require_POST
def login_with_password(request):
    """
    Authenticate an existing user with email and password
    and return a JWT access token.
    """
    try:
        data = read_json_object(request)

        email = get_required_text(
            data,
            "email",
        ).lower()

        password = get_required_text(
            data,
            "password",
        )

    except ValueError as exc:
        return error_response(
            "invalid_request",
            str(exc),
        )

    user = get_auth_user_by_email(email)

    if user is None or not check_password(
        password,
        user["hashed_password"],
    ):
        return error_response(
            "invalid_credentials",
            "The email or password is incorrect.",
            status=401,
        )

    if user["account_status"] != "Active":
        return error_response(
            "account_inactive",
            "This user account is not active.",
            status=403,
        )

    access_token = create_access_token(
        phone_number=user["phone_number"],
        role=user["role"],
    )

    public_user = _build_public_user(user)

    return JsonResponse(
        {
            "message": "Login successful.",
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": (settings.JWT_ACCESS_TOKEN_MINUTES * 60),
            "user": public_user,
        },
        status=200,
    )


@csrf_exempt
@require_POST
def request_login_otp(request):
    """
    Send an email OTP for logging into an existing account.
    """
    try:
        data = read_json_object(request)

        email = get_required_text(
            data,
            "email",
        ).lower()

    except ValueError as exc:
        return error_response(
            "invalid_request",
            str(exc),
        )

    user = get_auth_user_by_email(email)

    if user is None:
        return error_response(
            "user_not_found",
            "No account exists with this email.",
            status=404,
        )

    if user["account_status"] != "Active":
        return error_response(
            "account_inactive",
            "This user account is not active.",
            status=403,
        )

    try:
        otp = generate_and_store_otp(
            email,
            OTP_PURPOSE_LOGIN,
        )

    except OTPCooldownError as exc:
        response = error_response(
            "otp_cooldown",
            "Please wait before requesting another login code.",
            status=429,
        )

        response["Retry-After"] = str(exc.retry_after)

        return response

    except OTPServiceUnavailableError:
        return error_response(
            "otp_service_unavailable",
            "The verification service is temporarily unavailable.",
            status=503,
        )

    try:
        send_otp_email(
            email,
            otp,
            OTP_PURPOSE_LOGIN,
        )

    except EmailDeliveryError:
        try:
            delete_otp(
                email,
                OTP_PURPOSE_LOGIN,
            )

        except OTPServiceUnavailableError:
            logger.exception(
                "Could not clean up login OTP for %s",
                email,
            )

        return error_response(
            "email_delivery_failed",
            "The login verification email could not be sent.",
            status=503,
        )

    return JsonResponse(
        {
            "message": ("A login verification code " "has been sent to your email."),
            "email": email,
            "expires_in": settings.OTP_TTL_SECONDS,
        },
        status=200,
    )


@csrf_exempt
@require_POST
def login_with_otp(request):
    """
    Authenticate an existing user with an email OTP
    and return a JWT access token.
    """
    try:
        data = read_json_object(request)

        email = get_required_text(
            data,
            "email",
        ).lower()

        otp = get_required_text(
            data,
            "otp",
        )

    except ValueError as exc:
        return error_response(
            "invalid_request",
            str(exc),
        )

    user = get_auth_user_by_email(email)

    if user is None:
        return error_response(
            "user_not_found",
            "No account exists with this email.",
            status=404,
        )

    if user["account_status"] != "Active":
        return error_response(
            "account_inactive",
            "This user account is not active.",
            status=403,
        )

    try:
        verify_otp_code(
            email,
            OTP_PURPOSE_LOGIN,
            otp,
        )

    except InvalidOTPError as exc:
        return error_response(
            "invalid_otp",
            str(exc),
            status=400,
        )

    except TooManyOTPAttemptsError as exc:
        return error_response(
            "too_many_otp_attempts",
            str(exc),
            status=429,
        )

    except OTPServiceUnavailableError:
        return error_response(
            "otp_service_unavailable",
            "The verification service is temporarily unavailable.",
            status=503,
        )

    access_token = create_access_token(
        phone_number=user["phone_number"],
        role=user["role"],
    )

    public_user = _build_public_user(user)

    return JsonResponse(
        {
            "message": "Login successful.",
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": (settings.JWT_ACCESS_TOKEN_MINUTES * 60),
            "user": public_user,
        },
        status=200,
    )
