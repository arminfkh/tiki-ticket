import json
import logging

from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.common.authentication import (
    InvalidAccessToken,
    get_authenticated_payload,
)

from .queries import (
    ReservationError,
    create_reservation,
    get_cancellation_quote,
    get_user_reservations,
)

logger = logging.getLogger(__name__)


ERROR_STATUS_CODES = {
    "USER_NOT_FOUND": 404,
    "USER_INACTIVE": 403,
    "USER_NOT_SPECTATOR": 403,
    "TICKET_NOT_FOUND": 404,
    "MATCH_STARTED": 409,
    "TICKET_SOLD_OUT": 409,
    "ACTIVE_RESERVATION_EXISTS": 409,
    "TICKET_ALREADY_RESERVED": 409,
    "TICKET_ALREADY_SOLD": 409,
    "RESERVATION_NOT_FOUND": 404,
    "RESERVATION_NOT_OWNED": 403,
    "RESERVATION_NOT_PAID": 409,
    "SUCCESSFUL_PAYMENT_NOT_FOUND": 409,
}


@csrf_exempt
def reserve_ticket(request):
    """
    POST /api/reservations/

    Create a ten-minute ticket reservation for the authenticated user.
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

    phone_number = payload["sub"]

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
    GET /api/reservations/user/

    List reservations belonging to the authenticated user.
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


# Show cancellation penalty


def cancellation_quote(request, reservation_id):
    """
    GET /api/reservations/<reservation_id>/cancellation-quote/

    Calculate the cancellation penalty for a reservation owned by the
    authenticated user.
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
        quote = get_cancellation_quote(
            reservation_id=reservation_id,
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
            status=ERROR_STATUS_CODES.get(
                error.code,
                400,
            ),
        )
    except DatabaseError:
        logger.exception("Database error while calculating a cancellation quote.")

        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "The cancellation quote could not "
                        "be calculated because of a "
                        "database error."
                    ),
                }
            },
            status=500,
        )
    except Exception:
        logger.exception("Unexpected cancellation quote error.")

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
            "message": "Cancellation penalty calculated successfully.",
            "cancellation_quote": quote,
        },
        status=200,
    )
