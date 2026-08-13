import { apiRequest } from "./client.js";

export function searchTickets(filters = {}, { signal } = {}) {
  const params = new URLSearchParams();

  const allowedFilters = [
    "sport",
    "team",
    "city",
    "venue",
    "ticket_class",
    "date",
    "min_price",
    "max_price",
    "sort",
  ];

  for (const key of allowedFilters) {
    const value = filters[key];

    if (value !== undefined && value !== null && value !== "") {
      params.set(key, value);
    }
  }

  const queryString = params.toString();
  const endpoint = queryString ? `/tickets/?${queryString}` : "/tickets/";

  return apiRequest(endpoint, { signal });
}

export function getTicketDetails(ticketId, { signal } = {}) {
  return apiRequest(`/tickets/${ticketId}/`, { signal });
}
