import json
import logging
import re

from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .queries import (
    ReservationError,
    create_reservation,
    get_user_reservations,
)

logger = logging.getLogger(__name__)

PHONE_NUMBER_PATTERN = re.compile(r"^09\d{9}$")


ERROR_STATUS_CODES = {
    "USER_NOT_FOUND": 404,
    "USER_INACTIVE": 403,
    "USER_NOT_SPECTATOR": 403,
    "TICKET_NOT_FOUND": 404,
    "MATCH_STARTED": 409,
    "TICKET_SOLD_OUT": 409,
    "ACTIVE_RESERVATION_EXISTS": 409,
}


@csrf_exempt
def reserve_ticket(request):
    """
    POST /api/reservations/

    Create a ten-minute ticket reservation.
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
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "error": {
                    "code": "INVALID_JSON",
                    "message": "The request body must contain valid JSON.",
                }
            },
            status=400,
        )

    if not isinstance(body, dict):
        return JsonResponse(
            {
                "error": {
                    "code": "INVALID_BODY",
                    "message": "The JSON body must be an object.",
                }
            },
            status=400,
        )

    ticket_id = body.get("ticket_id")
    phone_number = body.get("phone_number")

    if not isinstance(ticket_id, int) or isinstance(ticket_id, bool) or ticket_id <= 0:
        return JsonResponse(
            {
                "error": {
                    "code": "INVALID_TICKET_ID",
                    "message": "ticket_id must be a positive integer.",
                }
            },
            status=400,
        )

    if (
        not isinstance(phone_number, str)
        or PHONE_NUMBER_PATTERN.fullmatch(phone_number) is None
    ):
        return JsonResponse(
            {
                "error": {
                    "code": "INVALID_PHONE_NUMBER",
                    "message": (
                        "phone_number must contain 11 digits and start " "with 09."
                    ),
                }
            },
            status=400,
        )

    try:
        reservation = create_reservation(
            ticket_id=ticket_id,
            phone_number=phone_number,
        )
    except ReservationError as error:
        return JsonResponse(
            {
                "error": {
                    "code": error.code,
                    "message": error.message,
                }
            },
            status=ERROR_STATUS_CODES.get(error.code, 400),
        )
    except DatabaseError:
        logger.exception("Database error while reserving a ticket.")

        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "The reservation could not be created because "
                        "of a database error."
                    ),
                }
            },
            status=500,
        )
    except Exception:
        logger.exception("Unexpected error while reserving a ticket.")

        return JsonResponse(
            {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred.",
                }
            },
            status=500,
        )

    return JsonResponse(
        {
            "message": "Ticket reserved successfully.",
            "reservation": reservation,
        },
        status=201,
    )


def list_user_reservations(request):
    """
    GET /api/reservations/user/?phone_number=...
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

    phone_number = request.GET.get("phone_number", "").strip()

    if PHONE_NUMBER_PATTERN.fullmatch(phone_number) is None:
        return JsonResponse(
            {
                "error": {
                    "code": "INVALID_PHONE_NUMBER",
                    "message": (
                        "phone_number must contain 11 digits " "and start with 09."
                    ),
                }
            },
            status=400,
        )

    try:
        result = get_user_reservations(phone_number)

    except ReservationError as error:
        return JsonResponse(
            {
                "error": {
                    "code": error.code,
                    "message": error.message,
                }
            },
            status=ERROR_STATUS_CODES.get(error.code, 400),
        )

    except DatabaseError:
        logger.exception("Database error while listing user reservations.")

        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "Reservations could not be retrieved "
                        "because of a database error."
                    ),
                }
            },
            status=500,
        )

    except Exception:
        logger.exception("Unexpected error while listing user reservations.")

        return JsonResponse(
            {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred.",
                }
            },
            status=500,
        )

    return JsonResponse(
        {
            "phone_number": phone_number,
            "active_count": len(result["active_reservations"]),
            "history_count": len(result["reservation_history"]),
            "active_reservations": result["active_reservations"],
            "reservation_history": result["reservation_history"],
        },
        status=200,
    )
