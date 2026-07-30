import json
import re

from django.conf import settings
from django.contrib.auth.hashers import make_password
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

from .queries import create_user, get_signup_conflicts

PHONE_PATTERN = re.compile(r"^09\d{9}$")


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
