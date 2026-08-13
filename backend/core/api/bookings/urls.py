from django.urls import path

from .views import list_user_bookings

app_name = "bookings"


urlpatterns = [
    path(
        "",
        list_user_bookings,
        name="list-user-bookings",
    ),
]
