from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .queries import get_cities, get_venues


@require_GET
def list_cities(request):
    """
    Return the list of distinct cities containing venues.
    """
    cities = get_cities()

    return JsonResponse(
        {
            "count": len(cities),
            "cities": cities,
        }
    )


@require_GET
def list_venues(request):
    """
    Return all venues, optionally filtered by city.
    """
    city = request.GET.get("city")

    if city is not None:
        city = city.strip()

        if not city:
            return JsonResponse(
                {
                    "error": {
                        "code": "invalid_city",
                        "message": "The city parameter cannot be empty.",
                    }
                },
                status=400,
            )

    venues = get_venues(city)

    return JsonResponse(
        {
            "count": len(venues),
            "venues": venues,
        }
    )
