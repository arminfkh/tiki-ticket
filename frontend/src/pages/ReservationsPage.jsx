import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { NavLink, useNavigate } from "react-router";

import {
  cancelReservation,
  getCancellationQuote,
  getMyReservations,
} from "../api/reservations.js";

function formatDateTime(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat("en", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatPrice(value) {
  const price = Number(value);

  if (!Number.isFinite(price)) {
    return "—";
  }

  return price.toFixed(2);
}

function formatCountdown(totalSeconds) {
  const safeSeconds = Math.max(
    0,
    Number(totalSeconds) || 0,
  );

  const minutes = Math.floor(
    safeSeconds / 60,
  );

  const seconds =
    safeSeconds % 60;

  return `${String(minutes).padStart(
    2,
    "0",
  )}:${String(seconds).padStart(
    2,
    "0",
  )}`;
}

function ReservationCountdown({
  initialSeconds,
  onExpire,
}) {
  const [
    remainingSeconds,
    setRemainingSeconds,
  ] = useState(() =>
    Math.max(
      0,
      Number(initialSeconds) || 0,
    ),
  );

  const notifiedRef =
    useRef(false);

  const onExpireRef =
    useRef(onExpire);

  useEffect(() => {
    onExpireRef.current =
      onExpire;
  }, [onExpire]);

  useEffect(() => {
    const startingSeconds =
      Math.max(
        0,
        Number(initialSeconds) || 0,
      );

    notifiedRef.current =
      false;

    if (startingSeconds <= 0) {
      const timeout =
        window.setTimeout(() => {
          if (
            !notifiedRef.current
          ) {
            notifiedRef.current =
              true;

            onExpireRef.current?.();
          }
        }, 500);

      return () =>
        window.clearTimeout(
          timeout,
        );
    }

    const timer =
      window.setInterval(() => {
        setRemainingSeconds(
          (current) => {
            if (current <= 1) {
              if (
                !notifiedRef.current
              ) {
                notifiedRef.current =
                  true;

                window.setTimeout(
                  () => {
                    onExpireRef.current?.();
                  },
                  500,
                );
              }

              return 0;
            }

            return current - 1;
          },
        );
      }, 1000);

    return () =>
      window.clearInterval(timer);
  }, [initialSeconds]);

  const expired =
    remainingSeconds <= 0;

  return (
    <div
      className={`reservation-timer ${
        expired
          ? "reservation-timer-expired"
          : ""
      }`}
    >
      <span>
        {expired
          ? "Expired"
          : "Time left"}
      </span>

      <strong>
        {formatCountdown(
          remainingSeconds,
        )}
      </strong>
    </div>
  );
}

function StatusBadge({ status }) {
  const normalized =
    String(status || "")
      .trim()
      .toLowerCase();

  return (
    <span
      className={`reservation-status reservation-status-${normalized}`}
    >
      {status || "Unknown"}
    </span>
  );
}

function ReservationTicketInfo({
  reservation,
}) {
  return (
    <div className="reservation-ticket-info">
      <div className="reservation-match-line">
        <div>
          <span className="reservation-sport-label">
            {reservation.sport_type ||
              "Match"}
          </span>

          <h3>
            {reservation.home_team}
            <span>vs</span>
            {reservation.away_team}
          </h3>
        </div>

        <div className="reservation-history-top-actions">
          <NavLink
            className="reservation-report-button"
            to={`/report/${reservation.reservation_id}`}
            title="Report a problem"
            aria-label={`Report a problem with reservation ${reservation.reservation_id}`}
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M5 21V4m0 0h11l-1.5 3L16 10H5"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </NavLink>

          <StatusBadge
            status={reservation.status}
          />
        </div>
      </div>

      <div className="reservation-match-meta">
        <span>
          {formatDateTime(
            reservation.match_datetime,
          )}
        </span>

        <span>
          {reservation.venue_name}
        </span>

        <span>
          {reservation.venue_city}
        </span>

        {reservation.league_name && (
          <span>
            {
              reservation.league_name
            }
          </span>
        )}
      </div>

      <div className="reservation-ticket-facts">
        <div>
          <span>
            Ticket
          </span>

          <strong>
            #
            {
              reservation.ticket_id
            }
          </strong>
        </div>

        <div>
          <span>
            Class
          </span>

          <strong>
            {
              reservation.ticket_class
            }
          </strong>
        </div>

        <div>
          <span>
            Section
          </span>

          <strong>
            {reservation.seat_section ||
              "—"}
          </strong>
        </div>

        <div>
          <span>
            Row / Seat
          </span>

          <strong>
            {reservation.seat_row ||
              "—"}
            {" / "}
            {reservation.seat_number ||
              "—"}
          </strong>
        </div>

        <div>
          <span>
            Price
          </span>

          <strong className="reservation-price">
            {formatPrice(
              reservation.ticket_price,
            )}
          </strong>
        </div>
      </div>
    </div>
  );
}

function ActiveReservationCard({
  reservation,
  onCheckout,
  onExpired,
}) {
  return (
    <article className="reservation-card reservation-card-active">
      <div className="reservation-card-main">
        <div className="reservation-card-number">
          <span>
            Reservation
          </span>

          <strong>
            #
            {
              reservation.reservation_id
            }
          </strong>
        </div>

        <ReservationTicketInfo
          reservation={
            reservation
          }
        />
      </div>

      <div className="reservation-card-side">
      <ReservationCountdown
        key={`${reservation.reservation_id}-${reservation.remaining_seconds}`}
        initialSeconds={
          reservation.remaining_seconds
        }
        onExpire={
          onExpired
        }
      />

        <div className="reservation-side-info">
          <span>
            Reserved at
          </span>

          <strong>
            {formatDateTime(
              reservation.reserved_at,
            )}
          </strong>
        </div>

        <button
          type="button"
          className="button reservation-checkout-button"
          onClick={() =>
            onCheckout(
              reservation.reservation_id,
            )
          }
        >
          Proceed to payment
        </button>

        <small>
          Unpaid reservations expire
          automatically when the timer
          reaches zero.
        </small>
      </div>
    </article>
  );
}

function CancellationQuote({
  quote,
  cancelling,
  onCancel,
  onClose,
}) {
  if (!quote) {
    return null;
  }

  return (
    <div className="cancellation-quote">
      <div className="cancellation-quote-header">
        <div>
          <p className="eyebrow">
            Cancellation quote
          </p>

          <h4>
            Refund preview
          </h4>
        </div>

        <button
          type="button"
          className="reservation-icon-button"
          onClick={onClose}
          aria-label="Close cancellation quote"
        >
          ×
        </button>
      </div>

      <div className="cancellation-quote-grid">
        <div>
          <span>
            Paid amount
          </span>

          <strong>
            {formatPrice(
              quote.paid_amount,
            )}
          </strong>
        </div>

        <div>
          <span>
            Penalty
          </span>

          <strong>
            {
              quote.penalty_percentage
            }
            %
          </strong>
        </div>

        <div>
          <span>
            Penalty amount
          </span>

          <strong>
            {formatPrice(
              quote.penalty_amount,
            )}
          </strong>
        </div>

        <div className="cancellation-refund">
          <span>
            Refund
          </span>

          <strong>
            {formatPrice(
              quote.refund_amount,
            )}
          </strong>
        </div>
      </div>

      <p className="cancellation-reason">
        {quote.reason}
      </p>

      {quote.can_cancel ? (
        <div className="cancellation-actions">
          <button
            type="button"
            className="button button-danger"
            disabled={cancelling}
            onClick={onCancel}
          >
            {cancelling
              ? "Cancelling..."
              : "Confirm cancellation"}
          </button>

          <button
            type="button"
            className="button button-secondary"
            disabled={cancelling}
            onClick={onClose}
          >
            Keep ticket
          </button>
        </div>
      ) : (
        <div className="reservation-inline-error">
          This reservation can no
          longer be cancelled.
        </div>
      )}
    </div>
  );
}

function HistoryReservationCard({
  reservation,
  quoteState,
  cancellingId,
  onGetQuote,
  onCancel,
  onCloseQuote,
}) {
  const isPaid =
    reservation.status === "Paid";

  const quoteIsOpen =
    quoteState.reservationId ===
    reservation.reservation_id;

  return (
    <article className="reservation-history-card">
      <div className="reservation-history-top">
        <div>
          <span>
            Reservation #
            {
              reservation.reservation_id
            }
          </span>

          <strong>
            {reservation.home_team}
            <em> vs </em>
            {reservation.away_team}
          </strong>
        </div>

        <div className="reservation-history-top-actions">
          <NavLink
            className="reservation-report-button"
            to={`/report/${reservation.reservation_id}`}
            title="Report a problem"
            aria-label={`Report a problem with reservation ${reservation.reservation_id}`}
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M5 21V4m0 0h11l-1.5 3L16 10H5"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </NavLink>

          <StatusBadge
            status={reservation.status}
          />
        </div>
      </div>

      <div className="reservation-history-grid">
        <div>
          <span>
            Match
          </span>

          <strong>
            {formatDateTime(
              reservation.match_datetime,
            )}
          </strong>
        </div>

        <div>
          <span>
            Venue
          </span>

          <strong>
            {
              reservation.venue_name
            }
          </strong>
        </div>

        <div>
          <span>
            Ticket
          </span>

          <strong>
            #
            {
              reservation.ticket_id
            }
            {" · "}
            {
              reservation.ticket_class
            }
          </strong>
        </div>

        <div>
          <span>
            Seat
          </span>

          <strong>
            {reservation.seat_section ||
              "—"}
            {" · "}
            {reservation.seat_row ||
              "—"}
            /
            {reservation.seat_number ||
              "—"}
          </strong>
        </div>

        <div>
          <span>
            Price
          </span>

          <strong className="reservation-price">
            {formatPrice(
              reservation.ticket_price,
            )}
          </strong>
        </div>
      </div>

      {isPaid && (
        <div className="reservation-history-actions">
          <button
            type="button"
            className="button button-secondary"
            disabled={
              quoteState.loading &&
              quoteState.reservationId ===
                reservation.reservation_id
            }
            onClick={() =>
              onGetQuote(
                reservation.reservation_id,
              )
            }
          >
            {quoteState.loading &&
            quoteState.reservationId ===
              reservation.reservation_id
              ? "Calculating..."
              : "Cancel ticket"}
          </button>
        </div>
      )}

      {quoteIsOpen &&
        quoteState.error && (
          <div className="reservation-inline-error">
            {
              quoteState.error
            }
          </div>
        )}

      {quoteIsOpen &&
        quoteState.quote && (
          <CancellationQuote
            quote={
              quoteState.quote
            }
            cancelling={
              cancellingId ===
              reservation.reservation_id
            }
            onCancel={() =>
              onCancel(
                reservation.reservation_id,
              )
            }
            onClose={
              onCloseQuote
            }
          />
        )}
    </article>
  );
}

export default function ReservationsPage() {
  const navigate =
    useNavigate();

  const [
    reservations,
    setReservations,
  ] = useState({
    active: [],
    history: [],
    activeCount: 0,
    historyCount: 0,
  });

  const [loading, setLoading] =
    useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const hasLoadedRef =
    useRef(false);

  const expiryRefreshTimerRef =
    useRef(null);

  const [error, setError] =
    useState("");

  const [
    refreshVersion,
    setRefreshVersion,
  ] = useState(0);

  const [
    quoteState,
    setQuoteState,
  ] = useState({
    reservationId: null,
    loading: false,
    quote: null,
    error: "",
  });

  const [
    cancellingId,
    setCancellingId,
  ] = useState(null);

  const [
    actionMessage,
    setActionMessage,
  ] = useState("");

  useEffect(() => {
    const controller =
      new AbortController();

    const isInitialLoad =
      !hasLoadedRef.current;

    async function loadReservations() {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      setError("");

      try {
        const data =
          await getMyReservations({
            signal:
              controller.signal,
          });

        const active =
          data?.active_reservations ||
          [];

        const history =
          data?.reservation_history ||
          [];

        setReservations({
          active,
          history,
          activeCount:
            data?.active_count ??
            active.length,
          historyCount:
            data?.history_count ??
            history.length,
        });

        hasLoadedRef.current =
          true;
      } catch (requestError) {
        if (
          requestError.name !==
          "AbortError"
        ) {
          setError(
            requestError.message ||
              "Could not load your reservations.",
          );
        }
      } finally {
        if (
          !controller.signal.aborted
        ) {
          if (isInitialLoad) {
            setLoading(false);
          } else {
            setRefreshing(false);
          }
        }
      }
    }

    loadReservations();

    return () =>
      controller.abort();
  }, [refreshVersion]);

  const refreshReservations =
    useCallback(() => {
      setRefreshVersion(
        (current) =>
          current + 1,
      );
    }, []);

  const handleExpiredReservation =
    useCallback(() => {
      if (
        expiryRefreshTimerRef.current
      ) {
        return;
      }

      expiryRefreshTimerRef.current =
        window.setTimeout(() => {
          expiryRefreshTimerRef.current =
            null;

          refreshReservations();
        }, 700);
    }, [refreshReservations]);

  useEffect(() => {
    return () => {
      if (
        expiryRefreshTimerRef.current
      ) {
        window.clearTimeout(
          expiryRefreshTimerRef.current,
        );
      }
    };
  }, []);

  async function handleGetQuote(
    reservationId,
  ) {
    if (
      quoteState.reservationId ===
        reservationId &&
      quoteState.quote
    ) {
      setQuoteState({
        reservationId: null,
        loading: false,
        quote: null,
        error: "",
      });

      return;
    }

    setActionMessage("");

    setQuoteState({
      reservationId,
      loading: true,
      quote: null,
      error: "",
    });

    try {
      const data =
        await getCancellationQuote(
          reservationId,
        );

      setQuoteState({
        reservationId,
        loading: false,
        quote:
          data?.cancellation_quote ||
          null,
        error: "",
      });
    } catch (requestError) {
      setQuoteState({
        reservationId,
        loading: false,
        quote: null,
        error:
          requestError.message ||
          "Could not calculate the cancellation quote.",
      });
    }
  }

  async function handleCancel(
    reservationId,
  ) {
    setCancellingId(
      reservationId,
    );

    setActionMessage("");

    try {
      const data =
        await cancelReservation(
          reservationId,
        );

      const refund =
        data?.refund
          ?.refund_amount;

      setActionMessage(
        refund !==
          undefined &&
        refund !==
          null
          ? `Reservation cancelled. ${formatPrice(
              refund,
            )} was refunded to your wallet.`
          : "Reservation cancelled successfully.",
      );

      setQuoteState({
        reservationId: null,
        loading: false,
        quote: null,
        error: "",
      });

      refreshReservations();
    } catch (requestError) {
      setQuoteState(
        (current) => ({
          ...current,
          reservationId,
          loading: false,
          error:
            requestError.message ||
            "The reservation could not be cancelled.",
        }),
      );
    } finally {
      setCancellingId(
        null,
      );
    }
  }

  if (loading) {
    return (
      <section className="reservations-page">
        <div className="reservations-page-header">
          <p className="eyebrow">
            My reservations
          </p>

          <h1>
            Loading your tickets...
          </h1>
        </div>

        <div className="reservations-loading">
          <div className="ticket-details-loader" />

          <span>
            Fetching reservation data
          </span>
        </div>
      </section>
    );
  }

  return (
    <section className="reservations-page">
      <div className="reservations-page-header">
        <div>
          <p className="eyebrow">
            My reservations
          </p>

          <h1>
            Your match-day tickets
          </h1>

          <p>
            Pay active reservations
            before they expire, and
            manage your paid ticket
            history here.
          </p>
        </div>

        <button
          type="button"
          className="button button-secondary"
          onClick={
            refreshReservations
          }
          disabled={refreshing}
        >
          {refreshing
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </div>

      <div className="reservations-stats">
        <div>
          <span>
            Active
          </span>

          <strong>
            {
              reservations.activeCount
            }
          </strong>

          <small>
            Waiting for payment
          </small>
        </div>

        <div>
          <span>
            History
          </span>

          <strong>
            {
              reservations.historyCount
            }
          </strong>

          <small>
            Paid or cancelled
          </small>
        </div>
      </div>

      {error && (
        <div className="ticket-state ticket-state-error">
          {error}
        </div>
      )}

      {actionMessage && (
        <div className="reservation-success-message">
          <span aria-hidden="true">
            ✓
          </span>

          {
            actionMessage
          }
        </div>
      )}

      <div className="reservations-section">
        <div className="reservations-section-heading">
          <div>
            <p className="eyebrow">
              Active reservations
            </p>

            <h2>
              Complete your payment
            </h2>
          </div>

          <p>
            Active reservations are
            held temporarily and expire
            automatically.
          </p>
        </div>

        {reservations.active.length ===
        0 ? (
          <div className="reservations-empty">
            <div>
              <span aria-hidden="true">
                ◇
              </span>
            </div>

            <h3>
              No active reservations
            </h3>

            <p>
              Choose a match and reserve
              a ticket to see it here.
            </p>

            <button
              type="button"
              className="button"
              onClick={() =>
                navigate(
                  "/tickets/football",
                )
              }
            >
              Browse tickets
            </button>
          </div>
        ) : (
          <div className="active-reservations-list">
            {reservations.active.map(
              (reservation) => (
                <ActiveReservationCard
                  key={
                    reservation.reservation_id
                  }
                  reservation={
                    reservation
                  }
                  onExpired={
                    handleExpiredReservation
                  }
                  onCheckout={(
                    reservationId,
                  ) =>
                    navigate(
                      `/checkout/${reservationId}`,
                    )
                  }
                />
              ),
            )}
          </div>
        )}
      </div>

      <div className="reservations-section">
        <div className="reservations-section-heading">
          <div>
            <p className="eyebrow">
              Reservation history
            </p>

            <h2>
              Previous tickets
            </h2>
          </div>

          <p>
            Paid tickets can receive a
            cancellation quote before
            cancellation.
          </p>
        </div>

        {reservations.history.length ===
        0 ? (
          <div className="reservations-empty reservations-empty-compact">
            <h3>
              No reservation history
            </h3>

            <p>
              Paid, expired and cancelled
              reservations will appear
              here.
            </p>
          </div>
        ) : (
          <div className="reservation-history-list">
            {reservations.history.map(
              (reservation) => (
                <HistoryReservationCard
                  key={
                    reservation.reservation_id
                  }
                  reservation={
                    reservation
                  }
                  quoteState={
                    quoteState
                  }
                  cancellingId={
                    cancellingId
                  }
                  onGetQuote={
                    handleGetQuote
                  }
                  onCancel={
                    handleCancel
                  }
                  onCloseQuote={() =>
                    setQuoteState({
                      reservationId:
                        null,
                      loading: false,
                      quote: null,
                      error: "",
                    })
                  }
                />
              ),
            )}
          </div>
        )}
      </div>
    </section>
  );
}