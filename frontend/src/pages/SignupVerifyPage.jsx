import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";

import { verifySignup } from "../api/auth.js";
import useAuth from "../auth/useAuth.js";

export default function SignupVerifyPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const { completeAuthentication } = useAuth();

  const email = location.state?.email;
  const initialExpiresIn = location.state?.expiresIn ?? 0;

  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [secondsRemaining, setSecondsRemaining] =
    useState(initialExpiresIn);

  useEffect(() => {
    if (!email) {
      navigate("/signup", {
        replace: true,
      });
    }
  }, [email, navigate]);

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

  function handleOtpChange(event) {
    const value = event.target.value;

    if (/^\d*$/.test(value) && value.length <= 6) {
      setOtp(value);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!email) {
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      const response = await verifySignup(email, otp);

      completeAuthentication(response);

      navigate("/", {
        replace: true,
      });
    } catch (error) {
      setError(error.message || "Verification failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
  }

  if (!email) {
    return null;
  }

  return (
    <main className="page-container">
      <section className="auth-card">
        <p className="eyebrow">Email verification</p>

        <h1>Verify your account</h1>

        <p className="auth-description">
          We sent a verification code to{" "}
          <strong>{email}</strong>.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="otp">Verification code</label>

            <input
              id="otp"
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
              The verification code may have expired.
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
            {isSubmitting
              ? "Verifying..."
              : "Verify account"}
          </button>
        </form>

        <p className="auth-footer">
          Wrong email? <Link to="/signup">Start again</Link>
        </p>
      </section>
    </main>
  );
}