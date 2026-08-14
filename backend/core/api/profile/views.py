import json

from django.core.exceptions import (
    ValidationError,
)
from django.core.validators import (
    validate_email,
)
from django.db import (
    IntegrityError,
)
from django.http import (
    JsonResponse,
)
from django.views.decorators.csrf import (
    csrf_exempt,
)
from django.views.decorators.http import (
    require_http_methods,
)
from redis.exceptions import (
    RedisError,
)

from core.common.authentication import (
    InvalidAccessToken,
    get_authenticated_payload,
)
from core.common.redis_client import (
    redis_client,
)

from .queries import (
    get_profile,
    update_profile,
)

PROFILE_CACHE_TTL_SECONDS = 600


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


def _profile_cache_key(
    phone_number: str,
) -> str:
    return f"profile:user:" f"{phone_number}"


def _cache_profile(
    profile: dict,
) -> None:
    """
    Store an updated profile in Redis.

    GET requests intentionally read PostgreSQL directly so
    WalletBalance always reflects payment/refund changes.
    """
    try:
        redis_client.setex(
            _profile_cache_key(profile["phone_number"]),
            PROFILE_CACHE_TTL_SECONDS,
            json.dumps(
                profile,
                default=str,
                ensure_ascii=False,
            ),
        )
    except RedisError:
        pass


def _authenticate(
    request,
):
    try:
        payload = get_authenticated_payload(request)
    except InvalidAccessToken as exc:
        return (
            None,
            _error_response(
                "invalid_access_token",
                str(exc),
                status=401,
            ),
        )

    return (
        payload["sub"],
        None,
    )


def _get_current_profile(
    phone_number: str,
):
    profile = get_profile(phone_number)

    if profile is None:
        return (
            None,
            _error_response(
                "user_not_found",
                ("The authenticated user " "no longer exists."),
                status=404,
            ),
        )

    if profile["account_status"] != "Active":
        return (
            None,
            _error_response(
                "account_inactive",
                ("This user account " "is not active."),
                status=403,
            ),
        )

    return (
        profile,
        None,
    )


@csrf_exempt
@require_http_methods(
    [
        "GET",
        "PATCH",
    ]
)
def update_user_profile(
    request,
):
    """
    GET /api/profile/
        Return the authenticated user's profile and wallet balance.

    PATCH /api/profile/
        Update editable profile fields.

    The function name is kept unchanged so the existing urls.py
    does not need to be modified.
    """
    (
        phone_number,
        auth_error,
    ) = _authenticate(request)

    if auth_error:
        return auth_error

    if request.method == "GET":
        (
            profile,
            profile_error,
        ) = _get_current_profile(phone_number)

        if profile_error:
            return profile_error

        return JsonResponse(
            {
                "profile": profile,
            },
            status=200,
        )

    try:
        data = json.loads(request.body)
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return _error_response(
            "invalid_json",
            ("The request body must " "contain valid JSON."),
        )

    if not isinstance(
        data,
        dict,
    ):
        return _error_response(
            "invalid_json",
            ("The JSON request body " "must be an object."),
        )

    allowed_fields = {
        "email",
        "first_name",
        "last_name",
        "residence_city",
    }

    unknown_fields = set(data) - allowed_fields

    if unknown_fields:
        return _error_response(
            "unsupported_fields",
            ("These fields cannot be " "updated: " + ", ".join(sorted(unknown_fields))),
        )

    if not data:
        return _error_response(
            "no_changes",
            ("At least one profile " "field is required."),
        )

    changes = {}

    for (
        field_name,
        value,
    ) in data.items():
        if field_name == "residence_city":
            if value is not None:
                if not isinstance(
                    value,
                    str,
                ):
                    return _error_response(
                        "invalid_residence_city",
                        ("The residence_city " "field must be text " "or null."),
                    )

                value = value.strip() or None

                if value is not None and len(value) > 100:
                    return _error_response(
                        "invalid_residence_city",
                        ("The residence city " "cannot exceed " "100 characters."),
                    )

            changes[field_name] = value

            continue

        if not isinstance(
            value,
            str,
        ):
            return _error_response(
                f"invalid_{field_name}",
                (f"The {field_name} " "field must be text."),
            )

        value = value.strip()

        if not value:
            return _error_response(
                f"invalid_{field_name}",
                (f"The {field_name} " "field cannot be empty."),
            )

        changes[field_name] = value

    email = changes.get("email")

    if email is not None:
        email = email.lower()

        if len(email) > 255:
            return _error_response(
                "invalid_email",
                ("The email address " "is too long."),
            )

        try:
            validate_email(email)
        except ValidationError:
            return _error_response(
                "invalid_email",
                ("Enter a valid " "email address."),
            )

        changes["email"] = email

    first_name = changes.get("first_name")

    if first_name is not None and len(first_name) > 50:
        return _error_response(
            "invalid_first_name",
            ("The first name cannot " "exceed 50 characters."),
        )

    last_name = changes.get("last_name")

    if last_name is not None and len(last_name) > 50:
        return _error_response(
            "invalid_last_name",
            ("The last name cannot " "exceed 50 characters."),
        )

    (
        existing_profile,
        profile_error,
    ) = _get_current_profile(phone_number)

    if profile_error:
        return profile_error

    try:
        profile = update_profile(
            phone_number=phone_number,
            changes=changes,
        )
    except IntegrityError:
        return _error_response(
            "email_exists",
            ("Another account already " "uses this email address."),
            status=409,
        )

    if profile is None:
        return _error_response(
            "profile_update_failed",
            ("The profile could not " "be updated."),
            status=500,
        )

    _cache_profile(profile)

    return JsonResponse(
        {
            "message": ("Profile updated " "successfully."),
            "profile": profile,
        },
        status=200,
    )
