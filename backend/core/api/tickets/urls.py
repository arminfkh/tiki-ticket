from django.urls import path

from .views import search_tickets

app_name = "tickets"

urlpatterns = [
    path("", search_tickets, name="ticket-search"),
]
