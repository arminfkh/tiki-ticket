import json
import logging

from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.common.authentication import (
    InvalidAccessToken,
    get_authenticated_payload,
)

from .queries import PaymentError, process_payment

logger = logging.getLogger(__name__)


ALLOWED_PAYMENT_METHODS = {
    "Card",
    "Wallet",
    "Other",
}

ALLOWED_PAYMENT_RESULTS = {
    "Pending",
    "Success",
    "Failed",
}

ERROR_STATUS_CODES = {
    "USER_NOT_FOUND": 404,
    "USER_INACTIVE": 403,
    "USER_NOT_SPECTATOR": 403,
    "RESERVATION_NOT_FOUND": 404,
    "RESERVATION_NOT_OWNED": 403,
    "RESERVATION_ALREADY_PAID": 409,
    "RESERVATION_CANCELLED": 409,
    "RESERVATION_EXPIRED": 409,
    "MATCH_STARTED": 409,
    "PAYMENT_ALREADY_SUCCESSFUL": 409,
}


@csrf_exempt
def pay_for_reservation(request):
    """
    POST /api/payments/
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

    # Authenticate user using JWT.
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

    # The authenticated user's phone number comes from the JWT,
    # not from the request body.
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

    reservation_id = body.get("reservation_id")
    payment_method = body.get("payment_method")
    simulate_result = body.get("simulate_result")

    if (
        not isinstance(reservation_id, int)
        or isinstance(reservation_id, bool)
        or reservation_id <= 0
    ):
        return JsonResponse(
            {
                "error": {
                    "code": "INVALID_RESERVATION_ID",
                    "message": "reservation_id must be a positive integer.",
                }
            },
            status=400,
        )

    if payment_method not in ALLOWED_PAYMENT_METHODS:
        return JsonResponse(
            {
                "error": {
                    "code": "INVALID_PAYMENT_METHOD",
                    "message": "payment_method must be Card, Wallet, or Other.",
                }
            },
            status=400,
        )

    if simulate_result not in ALLOWED_PAYMENT_RESULTS:
        return JsonResponse(
            {
                "error": {
                    "code": "INVALID_PAYMENT_RESULT",
                    "message": ("simulate_result must be Pending, Success or Failed."),
                }
            },
            status=400,
        )

    try:
        result = process_payment(
            reservation_id=reservation_id,
            phone_number=phone_number,
            payment_method=payment_method,
            payment_status=simulate_result,
        )

    except PaymentError as error:
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
        logger.exception("Database error while processing a payment.")

        return JsonResponse(
            {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": (
                        "The payment could not be processed "
                        "because of a database error."
                    ),
                }
            },
            status=500,
        )

    except Exception:
        logger.exception("Unexpected error while processing a payment.")

        return JsonResponse(
            {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred.",
                }
            },
            status=500,
        )

    payment_status = result["payment"]["status"]

    if payment_status == "Pending":
        return JsonResponse(
            {
                "message": ("Payment is pending. " "The reservation remains active."),
                **result,
            },
            status=202,
        )

    if payment_status == "Failed":
        return JsonResponse(
            {
                "message": ("Payment failed. " "The reservation remains active."),
                **result,
            },
            status=402,
        )

    return JsonResponse(
        {
            "message": "Payment completed successfully.",
            **result,
        },
        status=201,
    )
