from django.urls import path

from .views import (
    support_cancel_reservation,
    support_overview,
)

app_name = "support"


urlpatterns = [
    path(
        "overview/",
        support_overview,
        name="support-overview",
    ),
    path(
        "reservations/<int:reservation_id>/cancel/",
        support_cancel_reservation,
        name="support-cancel-reservation",
    ),
]
