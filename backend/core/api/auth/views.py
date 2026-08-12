import json
import re
import logging

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import (
    validate_password,
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.common.authentication import create_access_token

from .queries import (
    create_user,
    get_signup_conflicts,
    get_user_for_otp,
    get_user_for_login,
)

from .otp_service import (
    InvalidOTPError,
    OTPCooldownError,
    OTPServiceUnavailableError,
    TooManyOTPAttemptsError,
    generate_and_store_otp,
    verify_otp_code,
)

PHONE_PATTERN = re.compile(r"^09\d{9}$")
logger = logging.getLogger(__name__)


def _error_response(
    code: str,
    message: str,
    *,
    status: int = 400,
) -> JsonResponse:
    return JsonResponse(
        {
            "error": {
                "code": code,
                "message": message,
            }
        },
        status=status,
    )


def _get_required_text(
    data: dict,
    field_name: str,
) -> str:
    """
    Read and clean one required text field.
    """
    value = data.get(field_name)

    if not isinstance(value, str):
        raise ValueError(f"The {field_name} field is required.")

    value = value.strip()

    if not value:
        raise ValueError(f"The {field_name} field cannot be empty.")

    return value


def _read_json_object(request) -> dict:
    """
    Read a JSON object from the request body.
    """
    try:
        data = json.loads(request.body)
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as exc:
        raise ValueError("The request body must contain valid JSON.") from exc

    if not isinstance(data, dict):
        raise ValueError("The JSON request body must be an object.")

    return data


# sign up
@csrf_exempt
@require_POST
def signup(request):
    """
    Register a spectator and return a JWT access token.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error_response(
            "invalid_json",
            "The request body must contain valid JSON.",
        )

    if not isinstance(data, dict):
        return _error_response(
            "invalid_json",
            "The JSON request body must be an object.",
        )

    try:
        phone_number = _get_required_text(
            data,
            "phone_number",
        )
        email = _get_required_text(data, "email").lower()
        first_name = _get_required_text(
            data,
            "first_name",
        )
        last_name = _get_required_text(
            data,
            "last_name",
        )
        password = _get_required_text(data, "password")
    except ValueError as exc:
        return _error_response(
            "invalid_field",
            str(exc),
        )

    residence_city = data.get("residence_city")

    if residence_city is not None:
        if not isinstance(residence_city, str):
            return _error_response(
                "invalid_residence_city",
                "The residence_city field must be text.",
            )

        residence_city = residence_city.strip() or None

    if not PHONE_PATTERN.fullmatch(phone_number):
        return _error_response(
            "invalid_phone_number",
            "The phone number must contain exactly 11 digits.",
        )

    if len(email) > 255:
        return _error_response(
            "invalid_email",
            "The email address is too long.",
        )

    try:
        validate_email(email)
    except ValidationError:
        return _error_response(
            "invalid_email",
            "Enter a valid email address.",
        )

    if len(first_name) > 50:
        return _error_response(
            "invalid_first_name",
            "The first name cannot exceed 50 characters.",
        )

    if len(last_name) > 50:
        return _error_response(
            "invalid_last_name",
            "The last name cannot exceed 50 characters.",
        )

    if residence_city is not None and len(residence_city) > 100:
        return _error_response(
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

    conflicts = get_signup_conflicts(
        phone_number,
        email,
    )

    if conflicts is None:
        return _error_response(
            "conflict_check_failed",
            "The account information could not be checked.",
            status=500,
        )

    if conflicts["phone_exists"]:
        return _error_response(
            "phone_number_exists",
            "An account already exists with this phone number.",
            status=409,
        )

    if conflicts["email_exists"]:
        return _error_response(
            "email_exists",
            "An account already exists with this email.",
            status=409,
        )

    hashed_password = make_password(password)

    try:
        user = create_user(
            phone_number=phone_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            residence_city=residence_city,
            hashed_password=hashed_password,
        )
    except IntegrityError:
        return _error_response(
            "user_exists",
            ("An account already exists with this phone number or email."),
            status=409,
        )

    if user is None:
        return _error_response(
            "user_creation_failed",
            "The user could not be created.",
            status=500,
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


# password login
@csrf_exempt
@require_POST
def login(request):
    """
    Authenticate an existing user with email and password
    and return a JWT access token.
    """
    try:
        data = _read_json_object(request)

        email = _get_required_text(
            data,
            "email",
        ).lower()

        password = _get_required_text(
            data,
            "password",
        )
    except ValueError as exc:
        return _error_response(
            "invalid_request",
            str(exc),
        )

    user = get_user_for_login(email)
    if user is None or not check_password(password, user["hashed_password"]):
        return _error_response(
            "invalid_credentials",
            "The email or password is incorrect.",
            status=401,
        )
    if user["account_status"] != "Active":
        return _error_response(
            "account_inactive",
            "This user account is not active.",
            status=403,
        )

    access_token = create_access_token(
        phone_number=user["phone_number"],
        role=user["role"],
    )

    # prevent leaking the passoword hash
    public_user = {
        "phone_number": user["phone_number"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "residence_city": user["residence_city"],
        "account_status": user["account_status"],
        "role": user["role"],
    }

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


# otp
@csrf_exempt
@require_POST
def request_otp(request):
    """
    Generate and store an OTP for an existing active user.
    """
    try:
        data = _read_json_object(request)

        phone_number = _get_required_text(
            data,
            "phone_number",
        )

    except ValueError as exc:
        return _error_response(
            "invalid_request",
            str(exc),
        )

    if not PHONE_PATTERN.fullmatch(phone_number):
        return _error_response(
            "invalid_phone_number",
            ("The phone number must contain " "11 digits and start with 09."),
        )

    user = get_user_for_otp(phone_number)

    if user is None:
        return _error_response(
            "user_not_found",
            "No user was found with this phone number.",
            status=404,
        )

    if user["account_status"] != "Active":
        return _error_response(
            "account_inactive",
            "This user account is not active.",
            status=403,
        )

    try:
        otp = generate_and_store_otp(phone_number)

    except OTPCooldownError as exc:
        response = _error_response(
            "otp_cooldown",
            ("Please wait before requesting " "another OTP."),
            status=429,
        )

        response["Retry-After"] = str(exc.retry_after)

        return response

    except OTPServiceUnavailableError:
        return _error_response(
            "otp_service_unavailable",
            "The OTP service is temporarily unavailable.",
            status=503,
        )

    response_data = {
        "message": "OTP generated successfully.",
        "expires_in": settings.OTP_TTL_SECONDS,
    }

    # Only for local development and Postman testing.
    if settings.DEBUG:
        response_data["debug_otp"] = otp

        logger.warning(
            "Development OTP for %s: %s",
            phone_number,
            otp,
        )

    return JsonResponse(
        response_data,
        status=200,
    )


@csrf_exempt
@require_POST
def verify_otp(request):
    """
    Verify an OTP and return a JWT access token.
    """
    try:
        data = _read_json_object(request)

        phone_number = _get_required_text(
            data,
            "phone_number",
        )

        otp = _get_required_text(
            data,
            "otp",
        )

    except ValueError as exc:
        return _error_response(
            "invalid_request",
            str(exc),
        )

    if not PHONE_PATTERN.fullmatch(phone_number):
        return _error_response(
            "invalid_phone_number",
            ("The phone number must contain " "11 digits and start with 09."),
        )

    if not otp.isdigit() or len(otp) != settings.OTP_LENGTH:
        return _error_response(
            "invalid_otp_format",
            (f"The OTP must contain exactly " f"{settings.OTP_LENGTH} digits."),
        )

    user = get_user_for_otp(phone_number)

    if user is None:
        return _error_response(
            "user_not_found",
            "No user was found with this phone number.",
            status=404,
        )

    if user["account_status"] != "Active":
        return _error_response(
            "account_inactive",
            "This user account is not active.",
            status=403,
        )

    try:
        verify_otp_code(
            phone_number,
            otp,
        )

    except InvalidOTPError:
        return _error_response(
            "invalid_otp",
            "The OTP is invalid or has expired.",
        )

    except TooManyOTPAttemptsError:
        return _error_response(
            "too_many_otp_attempts",
            ("Too many incorrect attempts. " "Request a new OTP."),
            status=429,
        )

    except OTPServiceUnavailableError:
        return _error_response(
            "otp_service_unavailable",
            "The OTP service is temporarily unavailable.",
            status=503,
        )

    access_token = create_access_token(
        phone_number=user["phone_number"],
        role=user["role"],
    )

    return JsonResponse(
        {
            "message": "Login successful.",
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": (settings.JWT_ACCESS_TOKEN_MINUTES * 60),
            "user": user,
        },
        status=200,
    )
