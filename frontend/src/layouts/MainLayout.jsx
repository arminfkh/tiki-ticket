import { NavLink, Outlet, useLocation } from "react-router";

import useAuth from "../auth/useAuth.js";

const SPORTS = [
  { label: "Football", path: "/tickets/football" },
  { label: "Basketball", path: "/tickets/basketball" },
  { label: "Volleyball", path: "/tickets/volleyball" },
];

export default function MainLayout() {
  const { isAuthenticated, role, user, logout } = useAuth();
  const location = useLocation();

  const ticketsActive = location.pathname.startsWith("/tickets");

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
          <div className="nav-dropdown">
            <NavLink
              className={`nav-dropdown-trigger ${
                ticketsActive ? "active" : ""
              }`}
              to="/tickets/football"
            >
              Tickets

              <span
                className="nav-dropdown-arrow"
                aria-hidden="true"
              >
                ▾
              </span>
            </NavLink>

            <div className="sport-menu">
              {SPORTS.map((sport) => (
                <NavLink key={sport.path} to={sport.path}>
                  {sport.label}
                </NavLink>
              ))}
            </div>
          </div>

          {role === "Spectator" && (
            <>
              <NavLink to="/reservations">
                Reservations
              </NavLink>

              <NavLink to="/bookings">
                Bookings
              </NavLink>

              <NavLink to="/profile">
                Profile
              </NavLink>
            </>
          )}

          {role === "Support" && (
            <NavLink to="/support">
              Support
            </NavLink>
          )}
        </nav>

        <div className="auth-actions">
          {isAuthenticated ? (
            <>
              <span className="user-label">
                {user?.first_name || user?.email}
              </span>

              <button
                className="button button-secondary"
                onClick={logout}
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink
                className="button button-secondary"
                to="/login"
              >
                Log in
              </NavLink>

              <NavLink
                className="button"
                to="/signup"
              >
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