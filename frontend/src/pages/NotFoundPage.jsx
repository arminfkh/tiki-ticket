import { Link } from "react-router";

import useAuth from "../auth/useAuth.js";

export default function NotFoundPage() {
  const { role } = useAuth();

  return (
    <div className="not-found-page">
      <section className="not-found-card">
        <div className="not-found-code">404</div>

        <p className="eyebrow">Page not found</p>

        <h1>Looks like this match doesn't exist.</h1>

        <p className="not-found-description">
          The page may have been moved, deleted, or the
          address might be incorrect.
        </p>

        <div className="not-found-actions">
          <Link className="button" to="/">
            Back home
          </Link>

          {role === "Support" ? (
            <Link
              className="button button-secondary"
              to="/support"
            >
              Support dashboard
            </Link>
          ) : (
            <Link
              className="button button-secondary"
              to="/tickets"
            >
              Browse tickets
            </Link>
          )}
        </div>
      </section>
    </div>
  );
}