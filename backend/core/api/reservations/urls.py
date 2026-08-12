from django.urls import path

from .views import (
    list_user_reservations,
    reserve_ticket,
)


app_name = "reservations"

urlpatterns = [
    path("", reserve_ticket, name="reserve-ticket"),
    path(
        "user/",
        list_user_reservations,
        name="list-user-reservations",
    ),
]