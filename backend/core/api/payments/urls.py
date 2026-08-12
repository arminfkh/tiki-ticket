from django.urls import path

from .views import pay_for_reservation

app_name = "payments"

urlpatterns = [
    path("", pay_for_reservation, name="pay-for-reservation"),
]
