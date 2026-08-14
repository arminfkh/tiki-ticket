import { NavLink, Outlet } from "react-router";

import useAuth from "../auth/useAuth.js";

export default function MainLayout() {
  const { isAuthenticated, role, user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="site-header">
      <NavLink
        className="brand tiki-logo"
        to="/"
        aria-label="TikiTicket home"
      >
        <span className="tiki-logo-first">Tiki</span>
        <span className="tiki-logo-second">Ticket</span>
      </NavLink>
        <nav className="main-nav" aria-label="Main navigation">
          <NavLink to="/tickets">Tickets</NavLink>

          {role === "Spectator" && (
            <>
              <NavLink to="/reservations">Reservations</NavLink>
              <NavLink to="/bookings">Bookings</NavLink>
              <NavLink to="/profile">Profile</NavLink>
            </>
          )}

          {role === "Support" && (
            <NavLink to="/support">Support</NavLink>
          )}
        </nav>

        <div className="auth-actions">
          {isAuthenticated ? (
            <>
              <span className="user-label">
                {user?.first_name || user?.email}
              </span>
              <button className="button button-secondary" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink className="button button-secondary" to="/login">
                Log in
              </NavLink>
              <NavLink className="button" to="/signup">
                Sign up
              </NavLink>
            </>
          )}
        </div>
      </header>

      <main className="page-container">
        <Outlet />
      </main>
    </div>
  );
}
