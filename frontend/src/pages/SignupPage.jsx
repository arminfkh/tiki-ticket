import { useState } from "react";
import { Link, useNavigate } from "react-router";

import { signup } from "../api/auth.js";

export default function SignupPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    phoneNumber: "",
    email: "",
    residenceCity: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [errorDetails, setErrorDetails] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setErrorDetails([]);
    setIsSubmitting(true);

    try {
      const response = await signup(form);

      navigate("/signup/verify", {
        state: {
          email: response.email,
          expiresIn: response.expires_in,
        },
      });
    } catch (error) {
      setError(error.message || "Signup failed.");

      if (Array.isArray(error.details)) {
        setErrorDetails(error.details);
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-container">
      <section className="auth-card">
        <p className="eyebrow">Account</p>

        <h1>Create account</h1>

        <p className="auth-description">
          Create a spectator account to reserve and purchase tickets.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="firstName">First name</label>

              <input
                id="firstName"
                name="firstName"
                type="text"
                value={form.firstName}
                onChange={handleChange}
                maxLength={50}
                autoComplete="given-name"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="lastName">Last name</label>

              <input
                id="lastName"
                name="lastName"
                type="text"
                value={form.lastName}
                onChange={handleChange}
                maxLength={50}
                autoComplete="family-name"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="phoneNumber">Phone number</label>

            <input
              id="phoneNumber"
              name="phoneNumber"
              type="tel"
              value={form.phoneNumber}
              onChange={handleChange}
              placeholder="09123456789"
              pattern="09[0-9]{9}"
              maxLength={11}
              autoComplete="tel"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>

            <input
              id="email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              maxLength={255}
              autoComplete="email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="residenceCity">
              Residence city{" "}
              <span className="optional-label">(optional)</span>
            </label>

            <input
              id="residenceCity"
              name="residenceCity"
              type="text"
              value={form.residenceCity}
              onChange={handleChange}
              maxLength={100}
              autoComplete="address-level2"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>

            <input
              id="password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              autoComplete="new-password"
              required
            />
          </div>

          {error && (
            <div className="form-error" role="alert">
              <p>{error}</p>

              {errorDetails.length > 0 && (
                <ul>
                  {errorDetails.map((detail) => (
                    <li key={detail}>{detail}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          <button
            className="button auth-submit"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </section>
    </main>
  );
}