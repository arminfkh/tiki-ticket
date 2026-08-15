import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useLocation,
  useNavigate,
  useParams,
} from "react-router";

import { reserveTicket } from "../api/reservations.js";
import { getTicketDetails } from "../api/tickets.js";
import useAuth from "../auth/useAuth.js";


function formatPrice(value) {
  const price = Number(value);

  if (!Number.isFinite(price)) {
    return "—";
  }

  return price.toFixed(2);
}


function formatMatchDate(value) {
  if (!value) {
    return "Date unavailable";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat("en", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}


function formatCountdown(totalSeconds) {
  const safeSeconds = Math.max(
    0,
    totalSeconds,
  );

  const minutes =
    Math.floor(safeSeconds / 60);

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


function getFacilityItems(facilities) {
  if (!facilities) {
    return [];
  }

  if (Array.isArray(facilities)) {
    return facilities
      .map(String)
      .filter(Boolean);
  }

  if (typeof facilities === "string") {
    return facilities.trim()
      ? [facilities.trim()]
      : [];
  }

  if (typeof facilities === "object") {
    return Object.entries(facilities)
      .filter(([, value]) => (
        value !== false &&
        value !== null &&
        value !== undefined &&
        value !== ""
      ))
      .map(([key, value]) => {
        const readableKey = key
          .replaceAll("_", " ")
          .replace(
            /\b\w/g,
            (character) =>
              character.toUpperCase(),
          );

        return value === true
          ? readableKey
          : `${readableKey}: ${value}`;
      });
  }

  return [];
}


function ReservationResult({
  reservation,
  onCheckout,
}) {
  const [remainingSeconds, setRemainingSeconds] =
    useState(() => (
      Math.max(
        0,
        Number(
          reservation.remaining_seconds,
        ) || 0,
      )
    ));

  useEffect(() => {
    const timer =
      window.setInterval(() => {
        setRemainingSeconds(
          (current) => {
            if (current <= 1) {
              window.clearInterval(
                timer,
              );

              return 0;
            }

            return current - 1;
          },
        );
      }, 1000);

    return () =>
      window.clearInterval(timer);
  }, []);

  const expired =
    remainingSeconds <= 0;

  return (
    <div
      className={`reservation-success-card ${
        expired ? "expired" : ""
      }`}
    >
      <div
        className="reservation-success-icon"
        aria-hidden="true"
      >
        {expired ? "!" : "✓"}
      </div>

      <div className="reservation-success-copy">
        <p className="ticket-selection-eyebrow">
          {expired
            ? "Reservation expired"
            : "Reservation confirmed"}
        </p>

        <h4>
          {expired
            ? "The payment window has ended"
            : "Your ticket is reserved"}
        </h4>

        <p>
          Reservation #
          {reservation.reservation_id}
          {" · "}
          Ticket #
          {reservation.ticket_id}
        </p>
      </div>

      <div className="reservation-countdown">
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

        <small>
          {expired
            ? "The reservation window has ended."
            : "Complete payment before this timer reaches zero."}
        </small>
      </div>

      <div className="reservation-success-actions">
        {!expired && (
          <button
            className="button"
            type="button"
            onClick={onCheckout}
          >
            Proceed to payment
          </button>
        )}

        <Link
          className="button button-secondary"
          to="/reservations"
        >
          My reservations
        </Link>
      </div>
    </div>
  );
}


export default function TicketDetailsPage({
  ticketIdOverride = null,
}) {
  const navigate = useNavigate();
  const location = useLocation();

  const {
    sport: sportParam,
    ticketId: routeTicketId,
  } = useParams();

  const {
    isAuthenticated,
    role,
  } = useAuth();

  const ticketId =
    ticketIdOverride ??
    routeTicketId;

  const [ticket, setTicket] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [reserving, setReserving] =
    useState(false);

  const [
    reservationError,
    setReservationError,
  ] = useState("");

  const [reservation, setReservation] =
    useState(null);


  useEffect(() => {
    if (!ticketId) {
      return undefined;
    }

    const controller =
      new AbortController();

    async function loadTicket() {
      setLoading(true);
      setError("");

      try {
        const response =
          await getTicketDetails(
            ticketId,
            {
              signal:
                controller.signal,
            },
          );

        setTicket(
          response?.ticket ?? null,
        );
      } catch (requestError) {
        if (
          requestError.name !==
          "AbortError"
        ) {
          setError(
            requestError.message ||
              "Could not load ticket details.",
          );
        }
      } finally {
        if (
          !controller.signal.aborted
        ) {
          setLoading(false);
        }
      }
    }

    loadTicket();

    return () =>
      controller.abort();
  }, [ticketId]);


  function handleLogin() {
    navigate("/login", {
      state: {
        from: `${location.pathname}${location.search}${location.hash}`,
      },
    });
  }


  async function handleReserve() {
    if (!ticketId) {
      return;
    }

    if (!isAuthenticated) {
      handleLogin();
      return;
    }

    if (role !== "Spectator") {
      setReservationError(
        "Only spectator accounts can reserve tickets.",
      );

      return;
    }

    setReserving(true);
    setReservationError("");

    try {
      const response =
        await reserveTicket(ticketId);

      const createdReservation =
        response?.reservation;

      if (!createdReservation) {
        throw new Error(
          "The server did not return the created reservation.",
        );
      }

      setReservation(
        createdReservation,
      );

      setTicket((current) => {
        if (!current) {
          return current;
        }

        return {
          ...current,

          remaining_capacity:
            createdReservation.remained_capacity ??
            current.remaining_capacity,

          reservation_status:
            "Reserved",

          reservation_expires_at:
            createdReservation.expires_at,

          availability_status:
            "Reserved",

          is_available: false,
          is_selectable: false,
        };
      });
    } catch (requestError) {
      setReservationError(
        requestError.message ||
          "The ticket could not be reserved.",
      );
    } finally {
      setReserving(false);
    }
  }


  if (!ticketId) {
    return (
      <section className="ticket-state ticket-state-error">
        Invalid ticket address.
      </section>
    );
  }


  if (loading) {
    return (
      <section className="ticket-details-panel ticket-details-loading">
        <div className="ticket-details-loader" />

        <div>
          <strong>
            Loading ticket details
          </strong>

          <p>
            Getting the full information
            for this ticket.
          </p>
        </div>
      </section>
    );
  }


  if (error) {
    return (
      <section className="ticket-details-panel ticket-details-error">
        <strong>
          Could not load ticket
        </strong>

        <p>{error}</p>

        <Link
          className="button button-secondary"
          to="/tickets"
        >
          Back to tickets
        </Link>
      </section>
    );
  }


  if (!ticket) {
    return (
      <section className="ticket-state">
        Ticket not found.
      </section>
    );
  }


  const facilities =
    getFacilityItems(
      ticket.facilities,
    );

  const spectatorCanReserve =
    isAuthenticated &&
    role === "Spectator";

  const reserveDisabled =
    reserving ||
    !ticket.is_available ||
    Boolean(reservation);

  const ticketSport =
    String(
      ticket.sport ||
      sportParam ||
      "football",
    ).toLowerCase();

  const backToTickets =
    ["football", "basketball", "volleyball"]
      .includes(ticketSport)
      ? `/tickets/${ticketSport}`
      : "/tickets";


  return (
    <section className="tickets-page">
      <div>
        <Link
          className="report-back-link"
          to={backToTickets}
        >
          ← Back to tickets
        </Link>
      </div>

      <div className="ticket-details-panel">
        <div className="ticket-details-heading">
          <div>
            <p className="ticket-selection-eyebrow">
              Ticket details
            </p>

            <h4>
              {ticket.ticket_class ||
                "Match"}{" "}
              Ticket
            </h4>

            <p>
              {ticket.home_team || "—"}

              <span> vs </span>

              {ticket.away_team || "—"}
            </p>
          </div>

          <div
            className={`ticket-availability ${
              ticket.is_available
                ? "available"
                : "unavailable"
            }`}
          >
            <span />

            {ticket.is_available
              ? "Available"
              : "Unavailable"}
          </div>
        </div>


        <div className="ticket-details-grid">
          <div className="ticket-detail-item ticket-detail-price">
            <span>Price</span>

            <strong>
              {formatPrice(
                ticket.price,
              )}
            </strong>
          </div>

          <div className="ticket-detail-item">
            <span>Class</span>

            <strong>
              {ticket.ticket_class ||
                "—"}
            </strong>
          </div>

          <div className="ticket-detail-item">
            <span>Section</span>

            <strong>
              {ticket.seat_section ||
                "—"}
            </strong>
          </div>

          <div className="ticket-detail-item">
            <span>Row</span>

            <strong>
              {ticket.seat_row ||
                "—"}
            </strong>
          </div>

          <div className="ticket-detail-item">
            <span>Seat</span>

            <strong>
              {ticket.seat_number ||
                "—"}
            </strong>
          </div>

          <div className="ticket-detail-item">
            <span>
              Remaining capacity
            </span>

            <strong>
              {ticket.remaining_capacity ??
                "—"}
            </strong>
          </div>

          <div className="ticket-detail-item">
            <span>Venue</span>

            <strong>
              {ticket.venue || "—"}
            </strong>
          </div>

          <div className="ticket-detail-item">
            <span>City</span>

            <strong>
              {ticket.city || "—"}
            </strong>
          </div>
        </div>


        <div className="ticket-details-secondary">
          <div>
            <span>Match date</span>

            <strong>
              {formatMatchDate(
                ticket.match_datetime,
              )}
            </strong>
          </div>

          <div>
            <span>League</span>

            <strong>
              {ticket.league || "—"}
            </strong>
          </div>

          <div>
            <span>
              Venue capacity
            </span>

            <strong>
              {ticket.venue_capacity ??
                "—"}
            </strong>
          </div>
        </div>


        {facilities.length > 0 && (
          <div className="ticket-facilities">
            <span>Facilities</span>

            <div>
              {facilities.map(
                (facility) => (
                  <span
                    className="ticket-facility-chip"
                    key={facility}
                  >
                    {facility}
                  </span>
                ),
              )}
            </div>
          </div>
        )}


        <div className="ticket-reservation-area">
          {reservation ? (
            <ReservationResult
              key={
                reservation.reservation_id
              }
              reservation={
                reservation
              }
              onCheckout={() =>
                navigate(
                  `/checkout/${reservation.reservation_id}`,
                )
              }
            />
          ) : (
            <div className="ticket-reserve-card">
              <div>
                <p className="ticket-selection-eyebrow">
                  Ready to continue?
                </p>

                <h4>
                  Reserve this ticket for
                  10 minutes
                </h4>

                <p>
                  The reservation is
                  temporary. Complete
                  payment before it
                  expires.
                </p>
              </div>


              <div className="ticket-reserve-actions">
                {!isAuthenticated ? (
                  <button
                    className="button"
                    type="button"
                    onClick={
                      handleLogin
                    }
                  >
                    Log in to reserve
                  </button>
                ) : (
                  <button
                    className="button"
                    type="button"
                    onClick={
                      handleReserve
                    }
                    disabled={
                      reserveDisabled ||
                      !spectatorCanReserve
                    }
                  >
                    {reserving
                      ? "Reserving..."
                      : "Reserve this ticket"}
                  </button>
                )}


                {!isAuthenticated && (
                  <small>
                    You need a spectator
                    account to reserve
                    tickets.
                  </small>
                )}


                {isAuthenticated &&
                  role !== "Spectator" && (
                    <small>
                      Only spectator
                      accounts can reserve
                      tickets.
                    </small>
                  )}


                {isAuthenticated &&
                  role === "Spectator" &&
                  !ticket.is_available && (
                    <small>
                      This ticket is no
                      longer available for
                      reservation.
                    </small>
                  )}
              </div>
            </div>
          )}


          {reservationError &&
            !reservation && (
              <div
                className="ticket-reservation-error"
                role="alert"
              >
                <strong>
                  Reservation failed
                </strong>

                <span>
                  {reservationError}
                </span>
              </div>
            )}
        </div>
      </div>
    </section>
  );
}