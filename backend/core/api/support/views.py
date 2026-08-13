import logging

from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.common.authentication import (
    InvalidAccessToken,
    get_authenticated_payload,
)

from .queries import (
    SupportError,
    cancel_reservation_by_support,
    get_support_overview,
)

logger = logging.getLogger(__name__)


ERROR_STATUS_CODES = {
    "USER_NOT_FOUND": 404,
    "USER_INACTIVE": 403,
    "USER_NOT_SUPPORT": 403,
    "RESERVATION_NOT_FOUND": 404,
    "RESERVATION_ALREADY_CANCELLED": 409,
    "INVALID_RESERVATION_STATUS": 409,
    "SUCCESSFUL_PAYMENT_NOT_FOUND": 409,
    "MATCH_STARTED": 409,
}


def support_overview(request):
    """
    GET /api/support/overview/
    """

    if request.method != "GET":
        return JsonResponse(
            {
                "error": {
                    "code": "METHOD_NOT_ALLOWED",
                    "message": "Only GET requests are allowed.",
                }
            },
            status=405,
        )

    try:
        payload = get_authenticated_payload(request)
    except InvalidAccessToken as exc:
        return JsonResponse(
            {
                "error": {
                    "code": "invalid_access_token",
                    "message": str(exc),
                }
            },
            status=401,
        )

    support_phone_number = payload["sub"]

    try:
        result = get_support_overview(support_phone_number)

    except SupportError as error:
        return JsonResponse(
            {
                "error": {
                    "code": error.code,
                    "message": error.message,
                }
            },
            status=ERROR_STATUS_CODES.get(
                error.code,
                400,
            ),
        )

    except DatabaseError:
        logger.exception("Database error while retrieving support overview.")

        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "The support overview could not "
                        "be retrieved because of a "
                        "database error."
                    ),
                }
            },
            status=500,
        )

    except Exception:
        logger.exception("Unexpected support overview error.")

        return JsonResponse(
            {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": ("An unexpected server error occurred."),
                }
            },
            status=500,
        )

    return JsonResponse(
        {
            "cancelled_count": len(result["cancelled_tickets"]),
            "manageable_reservations_count": len(result["manageable_reservations"]),
            "suspicious_payments_count": len(result["suspicious_payments"]),
            "user_reports_count": len(result["user_reports"]),
            **result,
        },
        status=200,
    )


@csrf_exempt
def support_cancel_reservation(
    request,
    reservation_id,
):
    """
    POST /api/support/reservations/<reservation_id>/cancel/
    """

    if request.method != "POST":
        return JsonResponse(
            {
                "error": {
                    "code": "METHOD_NOT_ALLOWED",
                    "message": "Only POST requests are allowed.",
                }
            },
            status=405,
        )

    try:
        payload = get_authenticated_payload(request)
    except InvalidAccessToken as exc:
        return JsonResponse(
            {
                "error": {
                    "code": "invalid_access_token",
                    "message": str(exc),
                }
            },
            status=401,
        )

    support_phone_number = payload["sub"]

    try:
        result = cancel_reservation_by_support(
            reservation_id=reservation_id,
            support_phone_number=support_phone_number,
        )

    except SupportError as error:
        return JsonResponse(
            {
                "error": {
                    "code": error.code,
                    "message": error.message,
                }
            },
            status=ERROR_STATUS_CODES.get(
                error.code,
                400,
            ),
        )

    except DatabaseError:
        logger.exception("Database error while cancelling " "a reservation by support.")

        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "The reservation could not be "
                        "cancelled because of a database error."
                    ),
                }
            },
            status=500,
        )

    except Exception:
        logger.exception("Unexpected support cancellation error.")

        return JsonResponse(
            {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": ("An unexpected server error occurred."),
                }
            },
            status=500,
        )

    return JsonResponse(
        {
            "message": ("Reservation cancelled successfully by support."),
            **result,
        },
        status=200,
    )
