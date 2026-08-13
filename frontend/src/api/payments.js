import { apiRequest } from "./client.js";

export function payForReservation({
  reservationId,
  paymentMethod,
  simulateResult,
}) {
  const body = {
    reservation_id: reservationId,
    payment_method: paymentMethod,
  };

  if (paymentMethod !== "Wallet") {
    body.simulate_result = simulateResult;
  }

  return apiRequest("/payments/", {
    method: "POST",
    body,
    authenticated: true,
  });
}
