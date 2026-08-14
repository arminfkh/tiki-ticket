import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  useNavigate,
  useParams,
} from "react-router";

import {
  payForReservation,
} from "../api/payments.js";
import {
  getProfile,
} from "../api/profile.js";
import {
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

function CheckoutCountdown({
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

    setRemainingSeconds(
      startingSeconds,
    );

    notifiedRef.current =
      false;

    if (startingSeconds <= 0) {
      return undefined;
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

                onExpireRef.current?.();
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
      className={`checkout-countdown ${
        expired
          ? "checkout-countdown-expired"
          : ""
      }`}
    >
      <span>
        {expired
          ? "Reservation expired"
          : "Reservation expires in"}
      </span>

      <strong>
        {formatCountdown(
          remainingSeconds,
        )}
      </strong>
    </div>
  );
}

function PaymentMethodCard({
  method,
  title,
  description,
  selected,
  disabled = false,
  children,
  onSelect,
}) {
  return (
    <button
      type="button"
      className={`checkout-method-card ${
        selected
          ? "selected"
          : ""
      }`}
      disabled={disabled}
      onClick={() =>
        onSelect(method)
      }
    >
      <div className="checkout-method-radio">
        <span />
      </div>

      <div className="checkout-method-copy">
        <div className="checkout-method-title">
          <strong>
            {title}
          </strong>

          {disabled && (
            <small>
              Unavailable
            </small>
          )}
        </div>

        <p>
          {description}
        </p>

        {children}
      </div>
    </button>
  );
}

function PaymentSuccess({
  result,
  reservation,
  onReservations,
  onTickets,
}) {
  const payment =
    result?.payment || {};

  const issuedTicket =
    result?.issued_ticket || {};

  return (
    <div className="checkout-success">
      <div className="checkout-success-icon">
        ✓
      </div>

      <p className="eyebrow">
        Payment successful
      </p>

      <h1>
        Your ticket is confirmed
      </h1>

      <p className="checkout-success-description">
        Reservation #
        {reservation.reservation_id}
        {" "}has been paid successfully.
      </p>

      <div className="checkout-receipt">
        <div>
          <span>
            Payment ID
          </span>

          <strong>
            #
            {payment.payment_id}
          </strong>
        </div>

        <div>
          <span>
            Method
          </span>

          <strong>
            {payment.method}
          </strong>
        </div>

        <div>
          <span>
            Amount
          </span>

          <strong className="checkout-price">
            {formatPrice(
              payment.amount,
            )}
          </strong>
        </div>

        <div>
          <span>
            Ticket
          </span>

          <strong>
            #
            {issuedTicket.ticket_id ||
              reservation.ticket_id}
          </strong>
        </div>

        <div>
          <span>
            Class
          </span>

          <strong>
            {issuedTicket.ticket_class ||
              reservation.ticket_class}
          </strong>
        </div>

        <div>
          <span>
            Seat
          </span>

          <strong>
            {issuedTicket.seat_row ||
              reservation.seat_row ||
              "—"}
            {" / "}
            {issuedTicket.seat_number ||
              reservation.seat_number ||
              "—"}
          </strong>
        </div>
      </div>

      {payment.wallet_balance !==
        undefined &&
        payment.wallet_balance !==
          null && (
          <div className="checkout-wallet-after-payment">
            <span>
              Wallet balance
            </span>

            <strong>
              {formatPrice(
                payment.wallet_balance,
              )}
            </strong>
          </div>
        )}

      <div className="checkout-success-actions">
        <button
          type="button"
          className="button"
          onClick={onReservations}
        >
          My reservations
        </button>

        <button
          type="button"
          className="button button-secondary"
          onClick={onTickets}
        >
          Browse more tickets
        </button>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  const {
    reservationId,
  } = useParams();

  const navigate =
    useNavigate();

  const numericReservationId =
    Number(reservationId);

  const [
    reservation,
    setReservation,
  ] = useState(null);

  const [
    profile,
    setProfile,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  const [
    selectedMethod,
    setSelectedMethod,
  ] = useState("Wallet");

  const [
    paying,
    setPaying,
  ] = useState(false);

  const [
    paymentError,
    setPaymentError,
  ] = useState("");

  const [
    paymentResult,
    setPaymentResult,
  ] = useState(null);

  const [
    expired,
    setExpired,
  ] = useState(false);

  useEffect(() => {
    if (
      !Number.isInteger(
        numericReservationId,
      ) ||
      numericReservationId <= 0
    ) {
      setError(
        "Invalid reservation ID.",
      );
      setLoading(false);

      return undefined;
    }

    const controller =
      new AbortController();

    async function loadCheckout() {
      setLoading(true);
      setError("");

      try {
        const [
          reservationsData,
          profileData,
        ] = await Promise.all([
          getMyReservations({
            signal:
              controller.signal,
          }),
          getProfile({
            signal:
              controller.signal,
          }),
        ]);

        const allReservations = [
          ...(
            reservationsData
              ?.active_reservations ||
            []
          ),
          ...(
            reservationsData
              ?.reservation_history ||
            []
          ),
        ];

        const foundReservation =
          allReservations.find(
            (item) =>
              Number(
                item.reservation_id,
              ) ===
              numericReservationId,
          );

        if (!foundReservation) {
          throw new Error(
            "Reservation not found.",
          );
        }

        setReservation(
          foundReservation,
        );

        setProfile(
          profileData?.profile ||
            null,
        );

        if (
          foundReservation.status !==
          "Reserved"
        ) {
          setExpired(
            foundReservation.status ===
              "Cancelled",
          );
        } else {
          setExpired(
            Number(
              foundReservation
                .remaining_seconds,
            ) <= 0,
          );
        }
      } catch (requestError) {
        if (
          requestError.name !==
          "AbortError"
        ) {
          setError(
            requestError.message ||
              "Could not load checkout information.",
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

    loadCheckout();

    return () =>
      controller.abort();
  }, [numericReservationId]);

  const walletBalance =
    Number(
      profile?.wallet_balance ||
        0,
    );

  const ticketPrice =
    Number(
      reservation?.ticket_price ||
        0,
    );

  const walletHasEnough =
    walletBalance >=
    ticketPrice;

  const reservationIsPayable =
    reservation?.status ===
      "Reserved" &&
    !expired;

  const payButtonDisabled =
    paying ||
    !reservationIsPayable ||
    (
      selectedMethod ===
        "Wallet" &&
      !walletHasEnough
    );

  const paymentButtonLabel =
    useMemo(() => {
      if (paying) {
        return "Processing payment...";
      }

      return `Pay ${formatPrice(
        ticketPrice,
      )}`;
    }, [
      paying,
      ticketPrice,
    ]);

  async function handlePayment() {
    if (
      !reservation ||
      payButtonDisabled
    ) {
      return;
    }

    setPaying(true);
    setPaymentError("");

    try {
      const result =
        await payForReservation({
          reservationId:
            reservation.reservation_id,
          paymentMethod:
            selectedMethod,

          // Card and Other are simulated by
          // the existing backend payment API.
          simulateResult:
            selectedMethod ===
              "Wallet"
              ? undefined
              : "Success",
        });

      setPaymentResult(
        result,
      );

      if (
        result?.payment
          ?.wallet_balance !==
        undefined
      ) {
        setProfile(
          (current) => ({
            ...(current || {}),
            wallet_balance:
              result.payment
                .wallet_balance,
          }),
        );
      }
    } catch (requestError) {
      setPaymentError(
        requestError.message ||
          "Payment could not be completed.",
      );

      if (
        requestError.code ===
        "RESERVATION_EXPIRED"
      ) {
        setExpired(true);
      }
    } finally {
      setPaying(false);
    }
  }

  if (loading) {
    return (
      <section className="checkout-page">
        <div className="checkout-loading">
          <div className="ticket-details-loader" />

          <span>
            Preparing checkout...
          </span>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="checkout-page">
        <div className="checkout-state-card checkout-state-error">
          <p className="eyebrow">
            Checkout unavailable
          </p>

          <h1>
            We could not open this reservation
          </h1>

          <p>
            {error}
          </p>

          <button
            type="button"
            className="button"
            onClick={() =>
              navigate(
                "/reservations",
              )
            }
          >
            Back to reservations
          </button>
        </div>
      </section>
    );
  }

  if (paymentResult) {
    return (
      <section className="checkout-page">
        <PaymentSuccess
          result={
            paymentResult
          }
          reservation={
            reservation
          }
          onReservations={() =>
            navigate(
              "/reservations",
            )
          }
          onTickets={() =>
            navigate(
              "/tickets/football",
            )
          }
        />
      </section>
    );
  }

  const alreadyPaid =
    reservation?.status ===
    "Paid";

  return (
    <section className="checkout-page">
      <div className="checkout-header">
        <div>
          <p className="eyebrow">
            Secure checkout
          </p>

          <h1>
            Complete your payment
          </h1>

          <p>
            Review your reservation
            and choose a payment
            method.
          </p>
        </div>

        <button
          type="button"
          className="button button-secondary"
          onClick={() =>
            navigate(
              "/reservations",
            )
          }
        >
          Back to reservations
        </button>
      </div>

      <div className="checkout-layout">
        <div className="checkout-main">
          <div className="checkout-ticket-card">
            <div className="checkout-ticket-heading">
              <div>
                <p className="eyebrow">
                  Reservation #
                  {
                    reservation
                      .reservation_id
                  }
                </p>

                <h2>
                  {
                    reservation
                      .home_team
                  }

                  <span>
                    vs
                  </span>

                  {
                    reservation
                      .away_team
                  }
                </h2>
              </div>

              <span
                className={`reservation-status reservation-status-${String(
                  reservation.status,
                ).toLowerCase()}`}
              >
                {
                  reservation.status
                }
              </span>
            </div>

            <div className="checkout-ticket-meta">
              <span>
                {formatDateTime(
                  reservation
                    .match_datetime,
                )}
              </span>

              <span>
                {
                  reservation
                    .venue_name
                }
              </span>

              <span>
                {
                  reservation
                    .venue_city
                }
              </span>
            </div>

            <div className="checkout-ticket-facts">
              <div>
                <span>
                  Ticket
                </span>

                <strong>
                  #
                  {
                    reservation
                      .ticket_id
                  }
                </strong>
              </div>

              <div>
                <span>
                  Class
                </span>

                <strong>
                  {
                    reservation
                      .ticket_class
                  }
                </strong>
              </div>

              <div>
                <span>
                  Section
                </span>

                <strong>
                  {reservation
                    .seat_section ||
                    "—"}
                </strong>
              </div>

              <div>
                <span>
                  Row / Seat
                </span>

                <strong>
                  {reservation
                    .seat_row ||
                    "—"}
                  {" / "}
                  {reservation
                    .seat_number ||
                    "—"}
                </strong>
              </div>
            </div>
          </div>

          {reservationIsPayable && (
            <div className="checkout-payment-card">
              <div className="checkout-section-heading">
                <div>
                  <p className="eyebrow">
                    Payment method
                  </p>

                  <h2>
                    How would you like
                    to pay?
                  </h2>
                </div>
              </div>

              <div className="checkout-methods">
                <PaymentMethodCard
                  method="Wallet"
                  title="Wallet"
                  description="Pay instantly using your TikiTicket wallet balance."
                  selected={
                    selectedMethod ===
                    "Wallet"
                  }
                  onSelect={
                    setSelectedMethod
                  }
                >
                  <div className="checkout-wallet-balance">
                    <span>
                      Available balance
                    </span>

                    <strong>
                      {formatPrice(
                        walletBalance,
                      )}
                    </strong>
                  </div>

                  {!walletHasEnough && (
                    <div className="checkout-method-warning">
                      Insufficient wallet
                      balance for this
                      ticket.
                    </div>
                  )}
                </PaymentMethodCard>

                <PaymentMethodCard
                  method="Card"
                  title="Card"
                  description="Complete a simulated card payment for this database project."
                  selected={
                    selectedMethod ===
                    "Card"
                  }
                  onSelect={
                    setSelectedMethod
                  }
                >
                  <div className="checkout-method-note">
                    No card details are
                    stored. Your backend
                    simulates the gateway
                    result.
                  </div>
                </PaymentMethodCard>

                <PaymentMethodCard
                  method="Other"
                  title="Other"
                  description="Use the project's alternative simulated payment method."
                  selected={
                    selectedMethod ===
                    "Other"
                  }
                  onSelect={
                    setSelectedMethod
                  }
                >
                  <div className="checkout-method-note">
                    This method is also
                    completed through the
                    existing payment
                    simulation API.
                  </div>
                </PaymentMethodCard>
              </div>

              {paymentError && (
                <div
                  className="checkout-payment-error"
                  role="alert"
                >
                  <strong>
                    Payment failed
                  </strong>

                  <span>
                    {paymentError}
                  </span>
                </div>
              )}

              <button
                type="button"
                className="button checkout-pay-button"
                disabled={
                  payButtonDisabled
                }
                onClick={
                  handlePayment
                }
              >
                {
                  paymentButtonLabel
                }
              </button>
            </div>
          )}

          {!reservationIsPayable && (
            <div className="checkout-state-card checkout-reservation-closed">
              <p className="eyebrow">
                Payment unavailable
              </p>

              <h2>
                {alreadyPaid
                  ? "This reservation has already been paid"
                  : "This reservation is no longer active"}
              </h2>

              <p>
                {alreadyPaid
                  ? "Open My Reservations to view your paid ticket."
                  : "The reservation expired or was cancelled before payment."}
              </p>

              <button
                type="button"
                className="button"
                onClick={() =>
                  navigate(
                    "/reservations",
                  )
                }
              >
                My reservations
              </button>
            </div>
          )}
        </div>

        <aside className="checkout-sidebar">
          <div className="checkout-order-card">
            <p className="eyebrow">
              Order summary
            </p>

            <div className="checkout-order-row">
              <span>
                {
                  reservation
                    .ticket_class
                }{" "}
                ticket
              </span>

              <strong>
                {formatPrice(
                  ticketPrice,
                )}
              </strong>
            </div>

            <div className="checkout-order-row checkout-order-total">
              <span>
                Total
              </span>

              <strong>
                {formatPrice(
                  ticketPrice,
                )}
              </strong>
            </div>
          </div>

          {reservation.status ===
            "Reserved" && (
            <CheckoutCountdown
              initialSeconds={
                reservation
                  .remaining_seconds
              }
              onExpire={() =>
                setExpired(
                  true,
                )
              }
            />
          )}

          <div className="checkout-wallet-card">
            <span>
              Your wallet
            </span>

            <strong>
              {formatPrice(
                walletBalance,
              )}
            </strong>

            <small>
              Wallet payments are
              deducted atomically by
              the backend.
            </small>
          </div>
        </aside>
      </div>
    </section>
  );
}