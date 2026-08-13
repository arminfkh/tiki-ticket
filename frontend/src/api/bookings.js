import { apiRequest } from "./client.js";

export function getMyBookings({ signal } = {}) {
  return apiRequest("/bookings/", {
    authenticated: true,
    signal,
  });
}
