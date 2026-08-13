import { apiRequest } from "./client.js";

export function submitReport({
  reservationId,
  category,
  description,
}) {
  return apiRequest("/reports/", {
    method: "POST",
    authenticated: true,
    body: {
      reservation_id: reservationId,
      category,
      description,
    },
  });
}
