from django.urls import path

from .views import (
    cancellation_quote,
    cancel_reservation,
    list_user_reservations,
    reserve_ticket,
)

app_name = "reservations"


urlpatterns = [
    path(
        "",
        reserve_ticket,
        name="reserve-ticket",
    ),
    path(
        "user/",
        list_user_reservations,
        name="list-user-reservations",
    ),
    path(
        "<int:reservation_id>/cancellation-quote/",
        cancellation_quote,
        name="cancellation-quote",
    ),
    path(
        "<int:reservation_id>/cancel/",
        cancel_reservation,
        name="cancel-reservation",
    ),
]
