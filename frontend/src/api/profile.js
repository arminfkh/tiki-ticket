import { apiRequest } from "./client.js";

export function updateProfile(changes) {
  return apiRequest("/profile/", {
    method: "PATCH",
    body: changes,
    authenticated: true,
  });
}
