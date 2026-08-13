import re
import logging

from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError

from core.common.authentication import create_access_token

from ..common import *
from .queries import get_signup_conflicts, create_user
from ..otp_service import (
    InvalidOTPError,
    OTPCooldownError,
    OTPServiceUnavailableError,
    OTP_PURPOSE_SIGNUP,
    TooManyOTPAttemptsError,
    delete_otp,
    generate_and_store_otp,
    verify_otp_code,
)
from ..email_service import send_otp_email, EmailDeliveryError
from .service import (
    PendingSignupNotFoundError,
    SignupServiceUnavailableError,
    delete_pending_signup,
    get_pending_signup,
    store_pending_signup,
)

PHONE_PATTERN = re.compile(r"^09\d{9}$")
logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def signup(request):
    """
    Start spectator signup and send an email verification OTP.
    """
    try:
        data = read_json_object(request)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return error_response(
            "invalid_json",
            "The request body must contain valid JSON.",
        )

    if not isinstance(data, dict):
        return error_response(
            "invalid_json",
            "The JSON request body must be an object.",
        )

    try:

        # get phone number
        phone_number = get_required_text(
            data,
            "phone_number",
        )

        # get email
        email = get_required_text(data, "email").lower()

        # get first name
        first_name = get_required_text(
            data,
            "first_name",
        )

        # get last name
        last_name = get_required_text(
            data,
            "last_name",
        )

        # get password
        password = get_required_text(data, "password")

    except ValueError as exc:
        return error_response(
            "invalid_field",
            str(exc),
        )

    # get residence city
    residence_city = data.get("residence_city")

    # valid the data
    if residence_city is not None:
        if not isinstance(residence_city, str):
            return error_response(
                "invalid_residence_city",
                "The residence_city field must be text.",
            )

        residence_city = residence_city.strip() or None

    if not PHONE_PATTERN.fullmatch(phone_number):
        return error_response(
            "invalid_phone_number",
            "The phone number must contain exactly 11 digits.",
        )

    if len(email) > 255:
        return error_response(
            "invalid_email",
            "The email address is too long.",
        )

    try:
        validate_email(email)
    except ValidationError:
        return error_response(
            "invalid_email",
            "Enter a valid email address.",
        )

    if len(first_name) > 50:
        return error_response(
            "invalid_first_name",
            "The first name cannot exceed 50 characters.",
        )

    if len(last_name) > 50:
        return error_response(
            "invalid_last_name",
            "The last name cannot exceed 50 characters.",
        )

    if residence_city is not None and len(residence_city) > 100:
        return error_response(
            "invalid_residence_city",
            "The residence city cannot exceed 100 characters.",
        )

    try:
        validate_password(password)
    except ValidationError as exc:
        return JsonResponse(
            {
                "error": {
                    "code": "invalid_password",
                    "message": "The password is not acceptable.",
                    "details": exc.messages,
                }
            },
            status=400,
        )

    # check for duplicate account
    conflicts = get_signup_conflicts(phone_number, email)

    if conflicts is None:
        return error_response(
            "conflict_check_failed",
            "The account information could not be checked.",
            status=500,
        )

    if conflicts["phone_exists"] or conflicts["email_exists"]:
        return error_response(
            "account_exists",
            "An account already exists with this phone number or email.",
            status=409,
        )

    # hash password
    hashed_password = make_password(password)

    # generate the signup OTP
    try:
        otp = generate_and_store_otp(
            email,
            OTP_PURPOSE_SIGNUP,
        )

    except OTPCooldownError as exc:
        response = error_response(
            "otp_cooldown",
            "Please wait before requesting another verification code.",
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
        store_pending_signup(
            phone_number=phone_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            residence_city=residence_city,
            hashed_password=hashed_password,
        )

    except SignupServiceUnavailableError:
        try:
            delete_otp(
                email,
                OTP_PURPOSE_SIGNUP,
            )
        except OTPServiceUnavailableError:
            logger.exception(
                "Could not clean up signup OTP for %s",
                email,
            )

        return error_response(
            "signup_service_unavailable",
            "The signup service is temporarily unavailable.",
            status=503,
        )

    try:
        send_otp_email(
            email,
            otp,
            OTP_PURPOSE_SIGNUP,
        )

    except EmailDeliveryError:
        try:
            delete_pending_signup(email)
        except SignupServiceUnavailableError:
            logger.exception(
                "Could not clean up pending signup for %s",
                email,
            )

        try:
            delete_otp(
                email,
                OTP_PURPOSE_SIGNUP,
            )

        except OTPServiceUnavailableError:
            logger.exception(
                "Could not clean up signup OTP for %s",
                email,
            )

        return error_response(
            "email_delivery_failed",
            "The verification email could not be sent.",
            status=503,
        )

    return JsonResponse(
        {
            "message": ("A verification code has been sent to your email."),
            "email": email,
            "expires_in": settings.OTP_TTL_SECONDS,
        },
        # registration attempt accepted, but is not complete yet
        status=202,
    )


@csrf_exempt
@require_POST
def verify_signup(request):
    """
    Verify the signup OTP, create the user,
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

    # Load the registration data temporarily stored in Redis.
    try:
        pending_user = get_pending_signup(email)

    except PendingSignupNotFoundError as exc:
        return error_response(
            "pending_signup_not_found",
            str(exc),
            status=400,
        )

    except SignupServiceUnavailableError:
        return error_response(
            "signup_service_unavailable",
            "The signup service is temporarily unavailable.",
            status=503,
        )

    # Check again because another account may have been created
    # while this user was waiting for the OTP.
    conflicts = get_signup_conflicts(
        pending_user["phone_number"],
        pending_user["email"],
    )

    if conflicts is None:
        return error_response(
            "conflict_check_failed",
            "The account information could not be checked.",
            status=500,
        )

    if conflicts["phone_exists"] or conflicts["email_exists"]:
        try:
            delete_pending_signup(email)
            delete_otp(
                email,
                OTP_PURPOSE_SIGNUP,
            )

        except (
            SignupServiceUnavailableError,
            OTPServiceUnavailableError,
        ):
            logger.exception(
                "Could not completely clean up signup for %s",
                email,
            )

        return error_response(
            "account_exists",
            "An account already exists with this phone number or email.",
            status=409,
        )

    # Now verify and consume the one-time signup OTP.
    try:
        verify_otp_code(
            email,
            OTP_PURPOSE_SIGNUP,
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

    # OTP is valid: create the permanent PostgreSQL account.
    try:
        user = create_user(
            phone_number=pending_user["phone_number"],
            email=pending_user["email"],
            first_name=pending_user["first_name"],
            last_name=pending_user["last_name"],
            residence_city=pending_user["residence_city"],
            hashed_password=pending_user["hashed_password"],
        )

    except IntegrityError:
        try:
            delete_pending_signup(email)

        except SignupServiceUnavailableError:
            logger.exception(
                "Could not clean up pending signup for %s",
                email,
            )

        return error_response(
            "signup_conflict",
            "An account with this phone number or email already exists.",
            status=409,
        )

    # PostgreSQL creation succeeded. Redis cleanup failure
    # should not make us report signup as failed.
    try:
        delete_pending_signup(email)

    except SignupServiceUnavailableError:
        logger.exception(
            "Could not delete pending signup for %s",
            email,
        )

    access_token = create_access_token(
        phone_number=user["phone_number"],
        role=user["role"],
    )

    return JsonResponse(
        {
            "message": "User registered successfully.",
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": (settings.JWT_ACCESS_TOKEN_MINUTES * 60),
            "user": user,
        },
        status=201,
    )
