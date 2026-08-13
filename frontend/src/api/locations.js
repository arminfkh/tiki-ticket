import { apiRequest } from "./client.js";

export function getCities({ signal } = {}) {
  return apiRequest("/locations/cities/", { signal });
}

export function getVenues(city, { signal } = {}) {
  const params = new URLSearchParams();

  if (city) {
    params.set("city", city);
  }

  const queryString = params.toString();

  return apiRequest(
    queryString
      ? `/locations/venues/?${queryString}`
      : "/locations/venues/",
    { signal },
  );
}
