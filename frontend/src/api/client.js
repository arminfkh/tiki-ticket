import {
  expireAuthSession,
  getStoredToken,
} from "../auth/storage.js";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {
  constructor(
    message,
    {
      status,
      code,
      details,
      retryAfter,
    } = {},
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status ?? null;
    this.code = code ?? null;
    this.details = details ?? null;
    this.retryAfter = retryAfter ?? null;
  }
}

function getDefaultErrorMessage(status) {
  switch (status) {
    case 400:
      return "The request was invalid.";

    case 401:
      return "Authentication is required.";

    case 403:
      return "You do not have permission to perform this action.";

    case 404:
      return "The requested resource could not be found.";

    case 409:
      return "The request conflicts with the current state.";

    case 429:
      return "Too many requests. Please try again shortly.";

    case 500:
      return "The server encountered an unexpected error.";

    case 502:
      return "The backend server is currently unavailable.";

    case 503:
      return "The service is temporarily unavailable.";

    default:
      if (status >= 500) {
        return "The server could not complete the request.";
      }

      return "The request failed.";
  }
}

function readRetryAfter(response) {
  const value = response.headers.get("Retry-After");

  if (!value) {
    return null;
  }

  const seconds = Number(value);

  return Number.isFinite(seconds)
    ? seconds
    : value;
}

async function readResponseBody(response) {
  const rawBody = await response.text();

  if (!rawBody.trim()) {
    return {
      data: null,
      hasBody: false,
      isJson: true,
      parseFailed: false,
    };
  }

  const contentType =
    response.headers.get("Content-Type") || "";

  const trimmedBody = rawBody.trim();

  const looksLikeJson =
    contentType.includes("application/json") ||
    trimmedBody.startsWith("{") ||
    trimmedBody.startsWith("[");

  if (!looksLikeJson) {
    return {
      data: null,
      hasBody: true,
      isJson: false,
      parseFailed: false,
    };
  }

  try {
    return {
      data: JSON.parse(rawBody),
      hasBody: true,
      isJson: true,
      parseFailed: false,
    };
  } catch {
    return {
      data: null,
      hasBody: true,
      isJson: true,
      parseFailed: true,
    };
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
  const requestHeaders = {
    Accept: "application/json",
    ...headers,
  };

  let requestBody = body;

  if (
    body !== undefined &&
    body !== null &&
    !(body instanceof FormData)
  ) {
    requestHeaders["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  if (authenticated) {
    const token = getStoredToken();

    if (!token) {
      expireAuthSession();

      throw new ApiError(
        "Your session has expired. Please log in again.",
        {
          status: 401,
          code: "missing_access_token",
        },
      );
    }

    requestHeaders.Authorization = `Bearer ${token}`;
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method,
        headers: requestHeaders,
        body: requestBody,
        signal,
      },
    );
  } catch (error) {
    /*
     * AbortController is used by several pages.
     * Keep AbortError untouched so those pages can
     * continue checking error.name === "AbortError".
     */
    if (error?.name === "AbortError") {
      throw error;
    }

    throw new ApiError(
      "Could not connect to the server. Check your connection and try again.",
      {
        code: "network_error",
      },
    );
  }

  const {
    data,
    hasBody,
    isJson,
    parseFailed,
  } = await readResponseBody(response);

  const retryAfter = readRetryAfter(response);

  /*
   * Handle HTTP errors BEFORE complaining about HTML
   * or malformed JSON.
   *
   * This is what makes a proxy 502 show:
   * "The backend server is currently unavailable."
   *
   * instead of:
   * "invalid JSON response"
   */
  if (!response.ok) {
    if (authenticated && response.status === 401) {
      expireAuthSession();

      throw new ApiError(
        "Your session has expired. Please log in again.",
        {
          status: 401,
          code: "session_expired",
        },
      );
    }

    const serverError =
      data &&
      typeof data === "object" &&
      !Array.isArray(data)
        ? data.error
        : null;

    const serverMessage =
      serverError?.message ||
      (
        data &&
        typeof data === "object" &&
        !Array.isArray(data)
          ? data.message
          : null
      );

    throw new ApiError(
      serverMessage ||
        getDefaultErrorMessage(response.status),
      {
        status: response.status,
        code:
          serverError?.code ||
          `http_${response.status}`,
        details: serverError?.details,
        retryAfter,
      },
    );
  }

  /*
   * 204 No Content, or another successful endpoint
   * intentionally returning an empty body.
   */
  if (!hasBody) {
    return null;
  }

  /*
   * Our API contract is JSON. A successful response
   * containing HTML/text indicates a proxy/server
   * configuration problem.
   */
  if (!isJson || parseFailed) {
    throw new ApiError(
      "The server returned an unexpected response.",
      {
        status: response.status,
        code: "invalid_server_response",
      },
    );
  }

  return data;
}