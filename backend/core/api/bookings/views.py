import logging

from django.db import DatabaseError
from django.http import JsonResponse

from core.common.authentication import (
    InvalidAccessToken,
    get_authenticated_payload,
)

from .queries import (
    BookingError,
    get_user_bookings,
)

logger = logging.getLogger(__name__)


ERROR_STATUS_CODES = {
    "USER_NOT_FOUND": 404,
    "USER_INACTIVE": 403,
    "USER_NOT_SPECTATOR": 403,
}


def list_user_bookings(request):
    """
    GET /api/bookings/
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

    phone_number = payload["sub"]

    try:
        result = get_user_bookings(phone_number)

    except BookingError as error:
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
        logger.exception("Database error while retrieving user bookings.")

        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "The bookings could not be retrieved "
                        "because of a database error."
                    ),
                }
            },
            status=500,
        )

    except Exception:
        logger.exception("Unexpected error while retrieving user bookings.")

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
            "upcoming_count": len(result["upcoming_tickets"]),
            "cancelled_count": len(result["cancelled_tickets"]),
            "used_count": len(result["used_tickets"]),
            "upcoming_tickets": result["upcoming_tickets"],
            "cancelled_tickets": result["cancelled_tickets"],
            "used_tickets": result["used_tickets"],
        },
        status=200,
    )
