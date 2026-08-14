import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";

import {
  loginWithOtp,
  loginWithPassword,
  requestLoginOtp,
} from "../api/auth.js";
import useAuth from "../auth/useAuth.js";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const { completeAuthentication } = useAuth();

  const [loginMethod, setLoginMethod] = useState("password");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [otp, setOtp] = useState("");
  const [otpRequested, setOtpRequested] = useState(false);
  const [secondsRemaining, setSecondsRemaining] = useState(0);

  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (secondsRemaining <= 0) {
      return;
    }

    const timer = setInterval(() => {
      setSecondsRemaining((current) => {
        if (current <= 1) {
          clearInterval(timer);
          return 0;
        }

        return current - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [secondsRemaining]);

  function finishLogin(response) {
    completeAuthentication(response);

    const destination = location.state?.from || "/";

    navigate(destination, {
      replace: true,
    });
  }

  function changeLoginMethod(method) {
    setLoginMethod(method);
    setError("");
    setOtp("");
    setOtpRequested(false);
    setSecondsRemaining(0);
  }

  async function handlePasswordLogin(event) {
    event.preventDefault();

    setError("");
    setIsSubmitting(true);

    try {
      const response = await loginWithPassword(email, password);

      finishLogin(response);
    } catch (error) {
      setError(error.message || "Login failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRequestOtp(event) {
    event.preventDefault();

    setError("");
    setIsSubmitting(true);

    try {
      const response = await requestLoginOtp(email);

      setOtpRequested(true);
      setSecondsRemaining(response.expires_in ?? 0);
    } catch (error) {
      setError(error.message || "Could not send the login code.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleOtpLogin(event) {
    event.preventDefault();

    setError("");
    setIsSubmitting(true);

    try {
      const response = await loginWithOtp(email, otp);

      finishLogin(response);
    } catch (error) {
      setError(error.message || "Verification failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleOtpChange(event) {
    const value = event.target.value;

    if (/^\d*$/.test(value) && value.length <= 6) {
      setOtp(value);
    }
  }

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
  }

  return (
    <main className="page-container">
      <section className="auth-card">
        <p className="eyebrow">Account</p>

        <h1>Log in</h1>

        <p className="auth-description">
          Choose how you want to access your account.
        </p>

        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${
              loginMethod === "password" ? "auth-tab-active" : ""
            }`}
            onClick={() => changeLoginMethod("password")}
          >
            Password
          </button>

          <button
            type="button"
            className={`auth-tab ${
              loginMethod === "otp" ? "auth-tab-active" : ""
            }`}
            onClick={() => changeLoginMethod("otp")}
          >
            Email code
          </button>
        </div>

        {loginMethod === "password" && (
          <form className="auth-form" onSubmit={handlePasswordLogin}>
            <div className="form-group">
              <label htmlFor="password-email">Email</label>

              <input
                id="password-email"
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
        )}

        {loginMethod === "otp" && !otpRequested && (
          <form className="auth-form" onSubmit={handleRequestOtp}>
            <div className="form-group">
              <label htmlFor="otp-email">Email</label>

              <input
                id="otp-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <p className="auth-help">
              We'll send a one-time login code to your email.
            </p>

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
              {isSubmitting ? "Sending code..." : "Send login code"}
            </button>
          </form>
        )}

        {loginMethod === "otp" && otpRequested && (
          <form className="auth-form" onSubmit={handleOtpLogin}>
            <p className="auth-help">
              We sent a login code to <strong>{email}</strong>.
            </p>

            <div className="form-group">
              <label htmlFor="login-otp">Verification code</label>

              <input
                id="login-otp"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                value={otp}
                onChange={handleOtpChange}
                placeholder="123456"
                maxLength={6}
                required
              />
            </div>

            {secondsRemaining > 0 ? (
              <p className="otp-timer">
                Code expires in {formatTime(secondsRemaining)}
              </p>
            ) : (
              <p className="form-error">
                The login code may have expired.
              </p>
            )}

            {error && (
              <p className="form-error" role="alert">
                {error}
              </p>
            )}

            <button
              className="button auth-submit"
              type="submit"
              disabled={isSubmitting || otp.length !== 6}
            >
              {isSubmitting ? "Verifying..." : "Log in"}
            </button>

            <button
              className="auth-text-button"
              type="button"
              onClick={() => {
                setOtp("");
                setOtpRequested(false);
                setSecondsRemaining(0);
                setError("");
              }}
            >
              Use a different email
            </button>
          </form>
        )}

        <p className="auth-footer">
          Don't have an account? <Link to="/signup">Create one</Link>
        </p>
      </section>
    </main>
  );
}