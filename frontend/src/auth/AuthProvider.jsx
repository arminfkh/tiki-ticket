import { useState } from "react";

import AuthContext from "./AuthContext.js";
import {
  clearAuthSession,
  getStoredToken,
  getStoredUser,
  storeAuthSession,
  storeUser,
} from "./storage.js";

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(() => getStoredToken());
  const [user, setUser] = useState(() => getStoredUser());

  function completeAuthentication(authResponse) {
    const token = authResponse.access_token;
    const authenticatedUser = authResponse.user;

    storeAuthSession(token, authenticatedUser);
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
  }

  const value = {
    accessToken,
    user,
    isAuthenticated: Boolean(accessToken),
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
