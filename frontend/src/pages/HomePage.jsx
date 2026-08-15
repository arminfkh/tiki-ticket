import { Link, Navigate } from "react-router";

import useAuth from "../auth/useAuth.js";

export default function HomePage() {
  const {
    isAuthenticated,
    role,
    user,
  } = useAuth();

  if (isAuthenticated && role === "Support") {
    return <Navigate to="/support" replace />;
  }

  if (isAuthenticated && role === "Spectator") {
    return (
      <div className="home-page">
        <section className="home-hero">
          <p className="eyebrow">Match Tickets</p>

          <h1>
            Welcome back
            {user?.first_name
              ? `, ${user.first_name}`
              : ""}
          </h1>

          <p>
            Find matches, manage your reservations,
            and access your purchased tickets.
          </p>

          <div className="home-actions">
            <Link className="button" to="/tickets">
              Browse tickets
            </Link>

            <Link
              className="button button-secondary"
              to="/reservations"
            >
              My reservations
            </Link>
          </div>
        </section>

        <section className="home-grid">
          <HomeCard
            title="Find tickets"
            description="Search available matches and choose your ticket."
            to="/tickets"
            linkText="Browse tickets"
          />

          <HomeCard
            title="Reservations"
            description="View your active reservations and reservation history."
            to="/reservations"
            linkText="View reservations"
          />

          <HomeCard
            title="Profile"
            description="View and manage your account information."
            to="/profile"
            linkText="Open profile"
          />
        </section>
      </div>
    );
  }

  return (
    <div className="home-page">
      <section className="home-hero home-public-hero">
        <p className="eyebrow">Match Tickets</p>

        <h1>Your next match starts here.</h1>

        <p>
          Search sporting events, reserve your seat,
          and manage your tickets from one place.
        </p>

        <div className="home-actions">
          <Link className="button" to="/tickets">
            Browse tickets
          </Link>

          <Link
            className="button button-secondary"
            to="/login"
          >
            Log in
          </Link>

          <Link
            className="button button-secondary"
            to="/signup"
          >
            Create account
          </Link>
        </div>
      </section>

      <section className="home-grid">
        <article className="home-card">
          <span className="home-card-number">01</span>
          <h2>Find a match</h2>
          <p>
            Search sporting events by team, sport,
            location, date, and other filters.
          </p>
        </article>

        <article className="home-card">
          <span className="home-card-number">02</span>
          <h2>Choose your ticket</h2>
          <p>
            Select the ticket and seat that works
            best for you.
          </p>
        </article>

        <article className="home-card">
          <span className="home-card-number">03</span>
          <h2>Reserve and pay</h2>
          <p>
            Secure your reservation and complete
            payment through the application.
          </p>
        </article>
      </section>
    </div>
  );
}

function HomeCard({
  title,
  description,
  to,
  linkText,
}) {
  return (
    <article className="home-card">
      <h2>{title}</h2>

      <p>{description}</p>

      <Link className="home-card-link" to={to}>
        {linkText} →
      </Link>
    </article>
  );
}