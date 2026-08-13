import json

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.common.authentication import (
    InvalidAccessToken,
    get_authenticated_payload,
)

from .queries import (
    create_report,
    get_report_context,
)

REPORT_CATEGORIES = {
    "payment issue": "Payment Issue",
    "wrong information": "Wrong Information",
    "seat issue": "Seat Issue",
    "entry problem": "Entry Problem",
    "schedule change": "Schedule Change",
    "unexpected cancellation": "Unexpected Cancellation",
    "refund issue": "Refund Issue",
    "other": "Other",
}


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
    value = data.get(field_name)

    if not isinstance(value, str):
        raise ValueError(f"The {field_name} field is required.")

    value = value.strip()

    if not value:
        raise ValueError(f"The {field_name} field cannot be empty.")

    return value


@csrf_exempt
@require_POST
def submit_report(request):
    """
    Create a report for a reservation owned by the authenticated user.
    """
    try:
        payload = get_authenticated_payload(request)
    except InvalidAccessToken as exc:
        return _error_response(
            "invalid_access_token",
            str(exc),
            status=401,
        )

    phone_number = payload["sub"]

    try:
        data = json.loads(request.body)
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return _error_response(
            "invalid_json",
            "The request body must contain valid JSON.",
        )

    if not isinstance(data, dict):
        return _error_response(
            "invalid_json",
            "The JSON request body must be an object.",
        )

    reservation_id = data.get("reservation_id")

    if (
        not isinstance(reservation_id, int)
        or isinstance(reservation_id, bool)
        or reservation_id <= 0
    ):
        return _error_response(
            "invalid_reservation_id",
            "The reservation_id must be a positive integer.",
        )

    try:
        category = _get_required_text(
            data,
            "category",
        )
        description = _get_required_text(
            data,
            "description",
        )
    except ValueError as exc:
        return _error_response(
            "invalid_field",
            str(exc),
        )

    canonical_category = REPORT_CATEGORIES.get(category.casefold())

    if canonical_category is None:
        return _error_response(
            "invalid_category",
            (
                "Category must be Payment Issue, "
                "Wrong Information, Seat Issue, "
                "Entry Problem, Schedule Change, "
                "Unexpected Cancellation, Refund Issue, "
                "or Other."
            ),
        )

    if len(description) < 5:
        return _error_response(
            "description_too_short",
            ("The description must contain at least 5 characters."),
        )

    if len(description) > 2000:
        return _error_response(
            "description_too_long",
            ("The description cannot exceed 2000 characters."),
        )

    context = get_report_context(
        reservation_id=reservation_id,
        phone_number=phone_number,
    )

    if context is None:
        return _error_response(
            "user_not_found",
            "The authenticated user no longer exists.",
            status=404,
        )

    if context["account_status"] != "Active":
        return _error_response(
            "account_inactive",
            "This user account is not active.",
            status=403,
        )

    if context["role"] != "Spectator":
        return _error_response(
            "invalid_user_role",
            "Only spectator accounts can submit ticket reports.",
            status=403,
        )

    if context["reservation_id"] is None:
        return _error_response(
            "reservation_not_found",
            (
                "The reservation does not exist or does "
                "not belong to the authenticated user."
            ),
            status=404,
        )

    try:
        report = create_report(
            reservation_id=reservation_id,
            phone_number=phone_number,
            category=canonical_category,
            description=description,
        )
    except IntegrityError:
        return _error_response(
            "report_creation_failed",
            "The report could not be created.",
            status=409,
        )

    if report is None:
        return _error_response(
            "report_creation_failed",
            "The report could not be created.",
            status=500,
        )

    report["ticket"] = {
        "ticket_id": context["ticket_id"],
        "ticket_class": context["ticket_class"],
        "home_team": context["home_team"],
        "away_team": context["away_team"],
        "match_datetime": context["match_datetime"],
        "reservation_status": context["reservation_status"],
    }

    return JsonResponse(
        {
            "message": "Report submitted successfully.",
            "report": report,
        },
        status=201,
    )
