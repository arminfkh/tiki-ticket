import { getStoredToken } from "../auth/storage.js";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {
  constructor(message, { status, code, details } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export async function apiRequest(
  endpoint,
  {
    method = "GET",
    body,
    headers = {},
    authenticated = false,
    signal,
  } = {},
) {
  const requestHeaders = { ...headers };

  let requestBody = body;

  if (body !== undefined && body !== null && !(body instanceof FormData)) {
    requestHeaders["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  if (authenticated) {
    const token = getStoredToken();

    if (!token) {
      throw new ApiError("You must be logged in to perform this action.", {
        status: 401,
        code: "missing_access_token",
      });
    }

    requestHeaders.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: requestHeaders,
    body: requestBody,
    signal,
  });

  const rawBody = await response.text();
  let data = null;

  if (rawBody) {
    try {
      data = JSON.parse(rawBody);
    } catch {
      throw new ApiError("The server returned an invalid JSON response.", {
        status: response.status,
        code: "invalid_server_response",
      });
    }
  }

  if (!response.ok) {
    const serverError = data?.error;

    throw new ApiError(
      serverError?.message || data?.message || "The request failed.",
      {
        status: response.status,
        code: serverError?.code,
        details: serverError?.details,
      },
    );
  }

  return data;
}
