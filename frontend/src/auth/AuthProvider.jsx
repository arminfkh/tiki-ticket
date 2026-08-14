import {
  useLayoutEffect,
  useState,
} from "react";

import {
  useLocation,
  useNavigate,
} from "react-router";

import AuthContext from "./AuthContext.js";

import {
  AUTH_SESSION_EXPIRED_EVENT,
  clearAuthSession,
  getStoredToken,
  getStoredUser,
  storeAuthSession,
  storeUser,
} from "./storage.js";

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const location = useLocation();

  const [accessToken, setAccessToken] = useState(
    () => getStoredToken(),
  );

  const [user, setUser] = useState(
    () => getStoredUser(),
  );

  useLayoutEffect(() => {
    function handleSessionExpired() {
      setAccessToken(null);
      setUser(null);

      if (location.pathname === "/login") {
        return;
      }

      const from = [
        location.pathname,
        location.search,
        location.hash,
      ].join("");

      navigate("/login", {
        replace: true,
        state: {
          from,
        },
      });
    }

    window.addEventListener(
      AUTH_SESSION_EXPIRED_EVENT,
      handleSessionExpired,
    );

    return () => {
      window.removeEventListener(
        AUTH_SESSION_EXPIRED_EVENT,
        handleSessionExpired,
      );
    };
  }, [
    location.pathname,
    location.search,
    location.hash,
    navigate,
  ]);

  function completeAuthentication(authResponse) {
    const token = authResponse.access_token;
    const authenticatedUser = authResponse.user;

    storeAuthSession(
      token,
      authenticatedUser,
    );

    setAccessToken(token);
    setUser(authenticatedUser);
  }

  function updateUser(updatedUser) {
    storeUser(updatedUser);
    setUser(updatedUser);
  }

  function logout() {
    clearAuthSession();

    setAccessToken(null);
    setUser(null);

    navigate("/", {
      replace: true,
    });
  }

  const value = {
    accessToken,
    user,

    isAuthenticated: Boolean(
      accessToken && user,
    ),

    role: user?.role ?? null,

    completeAuthentication,
    updateUser,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}