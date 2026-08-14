import { useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
} from "react-router";

import { submitReport } from "../api/reports.js";

const REPORT_CATEGORIES = [
  "Payment Issue",
  "Wrong Information",
  "Seat Issue",
  "Entry Problem",
  "Schedule Change",
  "Unexpected Cancellation",
  "Refund Issue",
  "Other",
];

export default function ReportPage() {
  const { reservationId } = useParams();
  const navigate = useNavigate();

  const numericReservationId = Number(reservationId);

  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");

  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedReport, setSubmittedReport] = useState(null);

  const isValidReservationId =
    Number.isInteger(numericReservationId) &&
    numericReservationId > 0;

  async function handleSubmit(event) {
    event.preventDefault();

    if (!isValidReservationId) {
      setError("Invalid reservation ID.");
      return;
    }

    setError("");

    const trimmedDescription = description.trim();

    if (!category) {
      setError("Please select a report category.");
      return;
    }

    if (trimmedDescription.length < 5) {
      setError(
        "The description must contain at least 5 characters.",
      );
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await submitReport({
        reservationId: numericReservationId,
        category,
        description: trimmedDescription,
      });

      setSubmittedReport(response.report);
    } catch (error) {
      setError(
        error.message || "The report could not be submitted.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!isValidReservationId) {
    return (
      <div className="report-state-card">
        <h1>Invalid reservation</h1>

        <p>
          The reservation ID in this page is not valid.
        </p>

        <Link
          className="button"
          to="/reservations"
        >
          My reservations
        </Link>
      </div>
    );
  }

  if (submittedReport) {
    return (
      <div className="report-page">
        <section className="report-success-card">
          <div className="report-success-icon">
            ✓
          </div>

          <p className="eyebrow">
            Report submitted
          </p>

          <h1>Thanks for letting us know.</h1>

          <p>
            Your report has been submitted to the support
            team and is currently pending review.
          </p>

          <div className="report-success-details">
            <ReportInfo
              label="Report ID"
              value={`#${submittedReport.report_id}`}
            />

            <ReportInfo
              label="Reservation"
              value={`#${submittedReport.reservation_id}`}
            />

            <ReportInfo
              label="Category"
              value={submittedReport.category}
            />

            <ReportInfo
              label="Status"
              value={submittedReport.status}
            />
          </div>

          <div className="report-success-actions">
            <button
              className="button"
              type="button"
              onClick={() => navigate("/reservations")}
            >
              Back to reservations
            </button>

            <Link
              className="button button-secondary"
              to="/"
            >
              Home
            </Link>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="report-page">
      <div className="report-heading">
        <Link
          className="report-back-link"
          to="/reservations"
        >
          ← Back to reservations
        </Link>

        <p className="eyebrow">Support</p>

        <h1>Report a problem</h1>

        <p>
          Tell our support team about an issue with
          reservation #{reservationId}.
        </p>
      </div>

      <section className="report-card">
        <div className="report-reservation">
          <span>Reservation</span>

          <strong>#{reservationId}</strong>
        </div>

        <form
          className="report-form"
          onSubmit={handleSubmit}
        >
          <div className="form-group">
            <label htmlFor="report-category">
              What is the issue?
            </label>

            <select
              id="report-category"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value)
              }
              required
            >
              <option value="">
                Select a category
              </option>

              {REPORT_CATEGORIES.map((item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <div className="report-label-row">
              <label htmlFor="report-description">
                Description
              </label>

              <span>
                {description.length}/2000
              </span>
            </div>

            <textarea
              id="report-description"
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              placeholder="Describe what happened and include any useful details..."
              rows={7}
              minLength={5}
              maxLength={2000}
              required
            />

            <p className="report-help">
              Include enough information for support to
              understand the problem.
            </p>
          </div>

          {error && (
            <p
              className="form-error"
              role="alert"
            >
              {error}
            </p>
          )}

          <div className="report-actions">
            <Link
              className="button button-secondary"
              to="/reservations"
            >
              Cancel
            </Link>

            <button
              className="button"
              type="submit"
              disabled={
                isSubmitting ||
                !category ||
                description.trim().length < 5
              }
            >
              {isSubmitting
                ? "Submitting..."
                : "Submit report"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

function ReportInfo({ label, value }) {
  return (
    <div className="report-info">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}