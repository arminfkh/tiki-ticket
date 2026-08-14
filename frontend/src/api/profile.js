import { apiRequest } from "./client.js";

export function getProfile(
  { signal } = {},
) {
  return apiRequest("/profile/", {
    authenticated: true,
    signal,
  });
}

export function updateProfile(changes) {
  return apiRequest("/profile/", {
    method: "PATCH",
    body: changes,
    authenticated: true,
  });
}