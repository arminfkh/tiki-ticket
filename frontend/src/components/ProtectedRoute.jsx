import { Navigate, Outlet, useLocation } from "react-router";

import useAuth from "../auth/useAuth.js";

export default function ProtectedRoute({ allowedRoles }) {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: `${location.pathname}${location.search}${location.hash}`,
        }}
      />
    );
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
