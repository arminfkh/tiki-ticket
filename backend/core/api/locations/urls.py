from django.urls import path

from .views import list_cities, list_venues

app_name = "locations"

urlpatterns = [
    path("cities/", list_cities, name="city-list"),
    path("venues/", list_venues, name="venue-list"),
]
