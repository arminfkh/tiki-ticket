const TOKEN_KEY = "ticketing_access_token";
const USER_KEY = "ticketing_user";
const SESSION_EXPIRED_KEY = "ticketing_session_expired";

export const AUTH_SESSION_EXPIRED_EVENT =
  "ticketing:session-expired";

let sessionExpiryNotified = false;

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const rawUser = localStorage.getItem(USER_KEY);

  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function storeAuthSession(accessToken, user) {
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(USER_KEY, JSON.stringify(user));

  sessionStorage.removeItem(SESSION_EXPIRED_KEY);

  sessionExpiryNotified = false;
}

export function storeUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);

  sessionStorage.removeItem(SESSION_EXPIRED_KEY);

  sessionExpiryNotified = true;
}

export function expireAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);

  sessionStorage.setItem(
    SESSION_EXPIRED_KEY,
    "true",
  );

  if (sessionExpiryNotified) {
    return;
  }

  sessionExpiryNotified = true;

  window.dispatchEvent(
    new CustomEvent(AUTH_SESSION_EXPIRED_EVENT),
  );
}

export function consumeSessionExpiredNotice() {
  const sessionExpired =
    sessionStorage.getItem(SESSION_EXPIRED_KEY) === "true";

  if (sessionExpired) {
    sessionStorage.removeItem(SESSION_EXPIRED_KEY);
  }

  return sessionExpired;
}