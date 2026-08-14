import { useCallback, useEffect, useState } from "react";

import {
  getCancelledTickets,
  getManageableReservations,
  getSuspiciousPayments,
  getUserReports,
  reviewReport,
  supportCancelReservation,
} from "../api/support.js";

const TABS = [
  { id: "reports", label: "Reports" },
  { id: "reservations", label: "Reservations" },
  { id: "payments", label: "Payments" },
  { id: "cancelled", label: "Cancelled" },
];

export default function SupportDashboardPage() {
  const [activeTab, setActiveTab] = useState("reports");

  const [reports, setReports] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [payments, setPayments] = useState([]);
  const [cancelledTickets, setCancelledTickets] = useState([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [actionId, setActionId] = useState(null);

  const loadDashboard = useCallback(async (signal) => {
    setIsLoading(true);
    setError("");

    try {
      const [
        reportsResponse,
        reservationsResponse,
        paymentsResponse,
        cancelledResponse,
      ] = await Promise.all([
        getUserReports({ signal }),
        getManageableReservations({ signal }),
        getSuspiciousPayments({ signal }),
        getCancelledTickets({ signal }),
      ]);

      setReports(reportsResponse.user_reports ?? []);
      setReservations(reservationsResponse.reservations ?? []);
      setPayments(paymentsResponse.suspicious_payments ?? []);
      setCancelledTickets(
        cancelledResponse.cancelled_tickets ?? [],
      );
    } catch (error) {
      if (error.name !== "AbortError") {
        setError(
          error.message || "Could not load the support dashboard.",
        );
      }
    } finally {
      if (!signal?.aborted) {
        setIsLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    loadDashboard(controller.signal);

    return () => controller.abort();
  }, [loadDashboard]);

  async function handleReviewReport(reportId) {
    setError("");
    setSuccessMessage("");
    setActionId(`report-${reportId}`);

    try {
      await reviewReport(reportId);

      setReports((current) =>
        current.map((report) =>
          report.report_id === reportId
            ? {
                ...report,
                status: "Reviewed",
              }
            : report,
        ),
      );

      setSuccessMessage(
        `Report #${reportId} was marked as reviewed.`,
      );
    } catch (error) {
      setError(error.message || "Could not review the report.");
    } finally {
      setActionId(null);
    }
  }

  async function handleCancelReservation(reservation) {
    const confirmed = window.confirm(
      `Cancel reservation #${reservation.reservation_id} for ${reservation.home_team} vs ${reservation.away_team}?`,
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccessMessage("");
    setActionId(`reservation-${reservation.reservation_id}`);

    try {
      const response = await supportCancelReservation(
        reservation.reservation_id,
      );

      setSuccessMessage(
        response.refund
          ? `Reservation #${reservation.reservation_id} was cancelled and the allowed refund was added to the user's wallet.`
          : `Reservation #${reservation.reservation_id} was cancelled.`,
      );

      const controller = new AbortController();

      await loadDashboard(controller.signal);
    } catch (error) {
      setError(
        error.message || "Could not cancel the reservation.",
      );
    } finally {
      setActionId(null);
    }
  }

  function formatDate(value) {
    if (!value) {
      return "—";
    }

    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  }

  function formatPrice(value) {
    const number = Number(value);

    if (Number.isNaN(number)) {
      return value ?? "—";
    }

    return number.toLocaleString();
  }

  if (isLoading) {
    return (
      <section className="support-state-card">
        <p>Loading support dashboard...</p>
      </section>
    );
  }

  return (
    <div className="support-dashboard">
      <section className="support-heading">
        <div>
          <p className="eyebrow">Support</p>
          <h1>Support dashboard</h1>
          <p>
            Review reports, reservations, payments, and
            cancellations.
          </p>
        </div>
      </section>

      <section className="support-stats">
        <StatCard
          label="Pending reports"
          value={
            reports.filter((report) => report.status === "Pending")
              .length
          }
        />

        <StatCard
          label="Manageable reservations"
          value={reservations.length}
        />

        <StatCard
          label="Suspicious payments"
          value={payments.length}
        />

        <StatCard
          label="Cancelled tickets"
          value={cancelledTickets.length}
        />
      </section>

      {error && (
        <p className="support-alert support-alert-error" role="alert">
          {error}
        </p>
      )}

      {successMessage && (
        <p className="support-alert support-alert-success">
          {successMessage}
        </p>
      )}

      <div className="support-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`support-tab ${
              activeTab === tab.id ? "support-tab-active" : ""
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "reports" && (
        <section className="support-panel">
          <div className="support-panel-heading">
            <div>
              <h2>User reports</h2>
              <p>Review reports submitted by spectators.</p>
            </div>

            <span>{reports.length} total</span>
          </div>

          {reports.length === 0 ? (
            <EmptyState message="No reports were found." />
          ) : (
            <div className="support-list">
              {reports.map((report) => (
                <article
                  className="support-record"
                  key={report.report_id}
                >
                  <div className="support-record-heading">
                    <div>
                      <span className="support-record-id">
                        Report #{report.report_id}
                      </span>

                      <h3>{report.category}</h3>
                    </div>

                    <StatusBadge status={report.status} />
                  </div>

                  <div className="support-record-grid">
                    <Info
                      label="Submitted by"
                      value={report.submitter_phone_number}
                    />

                    <Info
                      label="Reservation"
                      value={`#${report.reservation_id}`}
                    />

                    <Info
                      label="Ticket"
                      value={`#${report.ticket_id} · ${report.ticket_class}`}
                    />

                    <Info
                      label="Match"
                      value={`${report.home_team} vs ${report.away_team}`}
                    />

                    <Info
                      label="Match date"
                      value={formatDate(report.match_datetime)}
                    />

                    <Info
                      label="Reservation status"
                      value={report.reservation_status}
                    />
                  </div>

                  <div className="support-description">
                    <span>Description</span>
                    <p>{report.description}</p>
                  </div>

                  <div className="support-record-actions">
                    <button
                      className="button"
                      type="button"
                      disabled={
                        report.status === "Reviewed" ||
                        actionId === `report-${report.report_id}`
                      }
                      onClick={() =>
                        handleReviewReport(report.report_id)
                      }
                    >
                      {actionId === `report-${report.report_id}`
                        ? "Reviewing..."
                        : report.status === "Reviewed"
                          ? "Reviewed"
                          : "Mark as reviewed"}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      {activeTab === "reservations" && (
        <section className="support-panel">
          <div className="support-panel-heading">
            <div>
              <h2>Manage reservations</h2>
              <p>
                Review active reserved and paid reservations.
              </p>
            </div>

            <span>{reservations.length} total</span>
          </div>

          {reservations.length === 0 ? (
            <EmptyState message="No manageable reservations were found." />
          ) : (
            <div className="support-list">
              {reservations.map((reservation) => (
                <article
                  className="support-record"
                  key={reservation.reservation_id}
                >
                  <div className="support-record-heading">
                    <div>
                      <span className="support-record-id">
                        Reservation #{reservation.reservation_id}
                      </span>

                      <h3>
                        {reservation.home_team} vs{" "}
                        {reservation.away_team}
                      </h3>
                    </div>

                    <StatusBadge status={reservation.status} />
                  </div>

                  <div className="support-record-grid">
                    <Info
                      label="User"
                      value={reservation.user_phone_number}
                    />

                    <Info
                      label="Ticket"
                      value={`#${reservation.ticket_id}`}
                    />

                    <Info
                      label="Class"
                      value={reservation.ticket_class}
                    />

                    <Info
                      label="Price"
                      value={formatPrice(reservation.ticket_price)}
                    />

                    <Info
                      label="Reserved at"
                      value={formatDate(reservation.reserved_at)}
                    />

                    <Info
                      label="Match date"
                      value={formatDate(reservation.match_datetime)}
                    />
                  </div>

                  <div className="support-record-actions">
                    <button
                      className="button support-danger-button"
                      type="button"
                      disabled={
                        reservation.match_started ||
                        actionId ===
                          `reservation-${reservation.reservation_id}`
                      }
                      onClick={() =>
                        handleCancelReservation(reservation)
                      }
                    >
                      {actionId ===
                      `reservation-${reservation.reservation_id}`
                        ? "Cancelling..."
                        : reservation.match_started
                          ? "Match started"
                          : "Cancel reservation"}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      {activeTab === "payments" && (
        <section className="support-panel">
          <div className="support-panel-heading">
            <div>
              <h2>Suspicious payments</h2>
              <p>Failed and pending payments requiring review.</p>
            </div>

            <span>{payments.length} total</span>
          </div>

          {payments.length === 0 ? (
            <EmptyState message="No suspicious payments were found." />
          ) : (
            <div className="support-list">
              {payments.map((payment) => (
                <article
                  className="support-record"
                  key={payment.payment_id}
                >
                  <div className="support-record-heading">
                    <div>
                      <span className="support-record-id">
                        Payment #{payment.payment_id}
                      </span>

                      <h3>
                        {payment.home_team} vs {payment.away_team}
                      </h3>
                    </div>

                    <StatusBadge status={payment.payment_status} />
                  </div>

                  <div className="support-record-grid">
                    <Info
                      label="User"
                      value={payment.user_phone_number}
                    />

                    <Info
                      label="Reservation"
                      value={`#${payment.reservation_id}`}
                    />

                    <Info
                      label="Ticket"
                      value={`#${payment.ticket_id}`}
                    />

                    <Info
                      label="Amount"
                      value={formatPrice(payment.amount)}
                    />

                    <Info
                      label="Method"
                      value={payment.payment_method}
                    />

                    <Info
                      label="Payment time"
                      value={formatDate(payment.payment_datetime)}
                    />
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      {activeTab === "cancelled" && (
        <section className="support-panel">
          <div className="support-panel-heading">
            <div>
              <h2>Cancelled tickets</h2>
              <p>Previously cancelled reservations and tickets.</p>
            </div>

            <span>{cancelledTickets.length} total</span>
          </div>

          {cancelledTickets.length === 0 ? (
            <EmptyState message="No cancelled tickets were found." />
          ) : (
            <div className="support-list">
              {cancelledTickets.map((ticket) => (
                <article
                  className="support-record"
                  key={ticket.reservation_id}
                >
                  <div className="support-record-heading">
                    <div>
                      <span className="support-record-id">
                        Reservation #{ticket.reservation_id}
                      </span>

                      <h3>
                        {ticket.home_team} vs {ticket.away_team}
                      </h3>
                    </div>

                    <StatusBadge status={ticket.status} />
                  </div>

                  <div className="support-record-grid">
                    <Info
                      label="User"
                      value={ticket.user_phone_number}
                    />

                    <Info
                      label="Cancelled by"
                      value={
                        ticket.cancellation_phone_number || "—"
                      }
                    />

                    <Info
                      label="Ticket"
                      value={`#${ticket.ticket_id} · ${ticket.ticket_class}`}
                    />

                    <Info
                      label="Seat"
                      value={[
                        ticket.seat_section,
                        ticket.seat_row,
                        ticket.seat_number,
                      ]
                        .filter(Boolean)
                        .join(" / ")}
                    />

                    <Info
                      label="Venue"
                      value={`${ticket.venue_name}, ${ticket.venue_city}`}
                    />

                    <Info
                      label="Match date"
                      value={formatDate(ticket.match_datetime)}
                    />
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <article className="support-stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function Info({ label, value }) {
  return (
    <div className="support-info">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function StatusBadge({ status }) {
  const normalized = status?.toLowerCase() ?? "";

  let className = "support-status";

  if (
    normalized === "pending" ||
    normalized === "reserved"
  ) {
    className += " support-status-warning";
  } else if (
    normalized === "reviewed" ||
    normalized === "paid" ||
    normalized === "success"
  ) {
    className += " support-status-success";
  } else if (
    normalized === "failed" ||
    normalized === "cancelled"
  ) {
    className += " support-status-danger";
  }

  return <span className={className}>{status}</span>;
}

function EmptyState({ message }) {
  return (
    <div className="support-empty">
      <p>{message}</p>
    </div>
  );
}