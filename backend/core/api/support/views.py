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
    get_cancelled_tickets,
    get_manageable_reservations,
    get_suspicious_payments,
    get_user_reports,
    review_report_by_support,
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


def authentication_error(exc):
    return JsonResponse(
        {
            "error": {
                "code": "invalid_access_token",
                "message": str(exc),
            }
        },
        status=401,
    )


def support_error_response(error):
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


def list_cancelled_tickets(request):
    """
    GET /api/support/cancelled-tickets/
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
        return authentication_error(exc)

    try:
        cancelled_tickets = get_cancelled_tickets(payload["sub"])

    except SupportError as error:
        return support_error_response(error)

    except DatabaseError:
        logger.exception("Database error while retrieving cancelled tickets.")
        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "Cancelled tickets could not be retrieved "
                        "because of a database error."
                    ),
                }
            },
            status=500,
        )

    return JsonResponse(
        {
            "count": len(cancelled_tickets),
            "cancelled_tickets": cancelled_tickets,
        },
        status=200,
    )


def list_suspicious_payments(request):
    """
    GET /api/support/suspicious-payments/
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
        return authentication_error(exc)

    try:
        suspicious_payments = get_suspicious_payments(payload["sub"])

    except SupportError as error:
        return support_error_response(error)

    except DatabaseError:
        logger.exception("Database error while retrieving suspicious payments.")
        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "Suspicious payments could not be retrieved "
                        "because of a database error."
                    ),
                }
            },
            status=500,
        )

    return JsonResponse(
        {
            "count": len(suspicious_payments),
            "suspicious_payments": suspicious_payments,
        },
        status=200,
    )


def list_user_reports(request):
    """
    GET /api/support/reports/
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
        return authentication_error(exc)

    try:
        user_reports = get_user_reports(payload["sub"])

    except SupportError as error:
        return support_error_response(error)

    except DatabaseError:
        logger.exception("Database error while retrieving user reports.")
        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "User reports could not be retrieved "
                        "because of a database error."
                    ),
                }
            },
            status=500,
        )

    return JsonResponse(
        {
            "count": len(user_reports),
            "user_reports": user_reports,
        },
        status=200,
    )


def list_manageable_reservations(request):
    """
    GET /api/support/reservations/
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
        return authentication_error(exc)

    try:
        reservations = get_manageable_reservations(payload["sub"])

    except SupportError as error:
        return support_error_response(error)

    except DatabaseError:
        logger.exception("Database error while retrieving support reservations.")
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

    return JsonResponse(
        {
            "count": len(reservations),
            "reservations": reservations,
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
        return authentication_error(exc)

    try:
        result = cancel_reservation_by_support(
            reservation_id=reservation_id,
            support_phone_number=payload["sub"],
        )

    except SupportError as error:
        return support_error_response(error)

    except DatabaseError:
        logger.exception("Database error while cancelling reservation by support.")
        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "The reservation could not be cancelled "
                        "because of a database error."
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


@csrf_exempt
def review_report(
    request,
    report_id,
):
    """
    POST /api/support/reports/<report_id>/review/
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
        return authentication_error(exc)

    try:
        report = review_report_by_support(
            report_id=report_id,
            support_phone_number=payload["sub"],
        )

    except SupportError as error:
        return support_error_response(error)

    except DatabaseError:
        logger.exception("Database error while reviewing report.")

        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "The report could not be reviewed "
                        "because of a database error."
                    ),
                }
            },
            status=500,
        )

    except Exception:
        logger.exception("Unexpected error while reviewing report.")

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
            "message": "Report reviewed successfully.",
            "report": report,
        },
        status=200,
    )
