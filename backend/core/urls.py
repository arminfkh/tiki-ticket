# core/urls.py

from django.urls import path, include

urlpatterns = [
    path('auth/', include('core.api.auth.urls')),
    path('bookings/', include('core.api.bookings.urls')),
    path('locations/', include('core.api.locations.urls')),
    path('payments/', include('core.api.payments.urls')),
    path('profile/', include('core.api.profile.urls')),
    path('reports/', include('core.api.reports.urls')),
    path('reservations/', include('core.api.reservations.urls')),
    path('support/', include('core.api.support.urls')),
    path('tickets/', include('core.api.tickets.urls')),
]