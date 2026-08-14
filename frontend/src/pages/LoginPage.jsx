import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";

import { loginWithPassword } from "../api/auth.js";
import useAuth from "../auth/useAuth.js";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const { completeAuthentication } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setIsSubmitting(true);

    try {
      const response = await loginWithPassword(email, password);

      completeAuthentication(response);

      const destination = location.state?.from || "/";

      navigate(destination, {
        replace: true,
      });
    } catch (error) {
      setError(error.message || "Login failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-container">
      <section className="auth-card">
        <p className="eyebrow">Account</p>

        <h1>Log in</h1>

        <p className="auth-description">
          Enter your email and password to continue.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <button
            className="button auth-submit"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Logging in..." : "Log in"}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/signup">Create one</Link>
        </p>
      </section>
    </main>
  );
}