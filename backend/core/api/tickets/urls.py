from django.urls import path

from .views import search_tickets, ticket_details

app_name = "tickets"

urlpatterns = [
    path("", search_tickets, name="ticket-search"),
    path("<int:ticket_id>/", ticket_details, name="ticket-details"),
]
