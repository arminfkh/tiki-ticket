from django.urls import path

from .views import (
    list_cancelled_tickets,
    list_manageable_reservations,
    list_suspicious_payments,
    list_user_reports,
    review_report,
    support_cancel_reservation,
)

app_name = "support"


urlpatterns = [
    path(
        "cancelled-tickets/",
        list_cancelled_tickets,
        name="cancelled-tickets",
    ),
    path(
        "suspicious-payments/",
        list_suspicious_payments,
        name="suspicious-payments",
    ),
    path(
        "reports/",
        list_user_reports,
        name="user-reports",
    ),
    path(
        "reservations/",
        list_manageable_reservations,
        name="manageable-reservations",
    ),
    path(
        "reservations/<int:reservation_id>/cancel/",
        support_cancel_reservation,
        name="cancel-reservation",
    ),
    path(
        "reports/<int:report_id>/review/",
        review_report,
        name="review-report",
    ),
]
