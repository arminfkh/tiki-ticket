from django.urls import path

from .views import (
    search_tickets,
    ticket_details,
    ticket_filter_options,
)

app_name = "tickets"

urlpatterns = [
    path(
        "",
        search_tickets,
        name="ticket-search",
    ),
    path(
        "filter-options/",
        ticket_filter_options,
        name="ticket-filter-options",
    ),
    path(
        "<int:ticket_id>/",
        ticket_details,
        name="ticket-details",
    ),
]
