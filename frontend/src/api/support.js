import { apiRequest } from "./client.js";

export function getCancelledTickets({ signal } = {}) {
  return apiRequest("/support/cancelled-tickets/", {
    authenticated: true,
    signal,
  });
}

export function getSuspiciousPayments({ signal } = {}) {
  return apiRequest("/support/suspicious-payments/", {
    authenticated: true,
    signal,
  });
}

export function getUserReports({ signal } = {}) {
  return apiRequest("/support/reports/", {
    authenticated: true,
    signal,
  });
}

export function getManageableReservations({ signal } = {}) {
  return apiRequest("/support/reservations/", {
    authenticated: true,
    signal,
  });
}

export function supportCancelReservation(reservationId) {
  return apiRequest(`/support/reservations/${reservationId}/cancel/`, {
    method: "POST",
    authenticated: true,
  });
}

export function reviewReport(reportId) {
  return apiRequest(`/support/reports/${reportId}/review/`, {
    method: "POST",
    authenticated: true,
  });
}
