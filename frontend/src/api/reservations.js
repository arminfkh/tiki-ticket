import { apiRequest } from "./client.js";

export function reserveTicket(ticketId) {
  return apiRequest("/reservations/", {
    method: "POST",
    body: { ticket_id: ticketId },
    authenticated: true,
  });
}

export function getMyReservations({ signal } = {}) {
  return apiRequest("/reservations/user/", {
    authenticated: true,
    signal,
  });
}

export function getCancellationQuote(reservationId, { signal } = {}) {
  return apiRequest(
    `/reservations/${reservationId}/cancellation-quote/`,
    {
      authenticated: true,
      signal,
    },
  );
}

export function cancelReservation(reservationId) {
  return apiRequest(`/reservations/${reservationId}/cancel/`, {
    method: "POST",
    authenticated: true,
  });
}
