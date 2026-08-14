import {
  useEffect,
  useMemo,
  useState,
} from "react";
import { useParams } from "react-router";

import {
  getTicketDetails,
  getTicketFilterOptions,
  searchTickets,
} from "../api/tickets.js";

import AutoCompleteInput from "../components/AutoCompleteInput.jsx";

const SPORT_CONFIG = {
  football: {
    label: "Football",
    subtitle: "Find your seat for the next big match.",
  },
  basketball: {
    label: "Basketball",
    subtitle: "Courtside energy, one ticket away.",
  },
  volleyball: {
    label: "Volleyball",
    subtitle: "Choose your match and get closer to the action.",
  },
};

const TICKET_CLASS_ORDER = [
  "vip",
  "premium",
  "regular",
];

const TICKET_CLASS_META = {
  vip: {
    label: "VIP",
    description: "VIP ticket options for this match.",
  },
  premium: {
    label: "Premium",
    description: "Premium ticket options for this match.",
  },
  regular: {
    label: "Regular",
    description: "Regular ticket options for this match.",
  },
};

const EMPTY_FILTERS = {
  team: "",
  city: "",
  venue: "",
  ticket_class: "",
  date: "",
  min_price: "",
  max_price: "",
  sort: "date_asc",
};

function normalize(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase();
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

function formatPrice(value) {
  const price = Number(value);

  if (!Number.isFinite(price)) {
    return "—";
  }

  return price.toFixed(2);
}

function getClassMeta(ticketClass) {
  const key = normalize(ticketClass);

  return (
    TICKET_CLASS_META[key] || {
      label: ticketClass || "Ticket",
      description: "Ticket options for this match.",
    }
  );
}

function getFacilityItems(facilities) {
  if (!facilities) {
    return [];
  }

  if (Array.isArray(facilities)) {
    return facilities
      .map((item) => String(item))
      .filter(Boolean);
  }

  if (typeof facilities === "string") {
    return facilities.trim()
      ? [facilities.trim()]
      : [];
  }

  if (
    typeof facilities === "object"
    && facilities !== null
  ) {
    return Object.entries(facilities)
      .filter(([, value]) => {
        return (
          value !== false
          && value !== null
          && value !== undefined
          && value !== ""
        );
      })
      .map(([key, value]) => {
        const readableKey = key
          .replaceAll("_", " ")
          .replace(/\b\w/g, (character) =>
            character.toUpperCase(),
          );

        if (value === true) {
          return readableKey;
        }

        return `${readableKey}: ${value}`;
      });
  }

  return [];
}

function SportArtwork({ sport }) {
  if (sport === "basketball") {
    return (
      <svg
        className="sport-hero-art"
        viewBox="0 0 520 220"
        aria-hidden="true"
      >
        <rect
          x="35"
          y="22"
          width="450"
          height="176"
          rx="18"
        />
        <line
          x1="260"
          y1="22"
          x2="260"
          y2="198"
        />
        <circle
          cx="260"
          cy="110"
          r="34"
        />
        <path d="M35 65h58v90H35M485 65h-58v90h58" />
        <path d="M93 84a52 52 0 0 1 0 52M427 84a52 52 0 0 0 0 52" />
        <circle
          cx="260"
          cy="110"
          r="82"
        />
      </svg>
    );
  }

  if (sport === "volleyball") {
    return (
      <svg
        className="sport-hero-art"
        viewBox="0 0 520 220"
        aria-hidden="true"
      >
        <rect
          x="35"
          y="35"
          width="450"
          height="150"
          rx="14"
        />
        <line
          x1="260"
          y1="35"
          x2="260"
          y2="185"
        />
        <line
          x1="210"
          y1="35"
          x2="210"
          y2="185"
        />
        <line
          x1="310"
          y1="35"
          x2="310"
          y2="185"
        />
        <line
          x1="35"
          y1="110"
          x2="485"
          y2="110"
        />
        <path d="M252 24v172M268 24v172" />
      </svg>
    );
  }

  return (
    <svg
      className="sport-hero-art"
      viewBox="0 0 520 220"
      aria-hidden="true"
    >
      <rect
        x="35"
        y="22"
        width="450"
        height="176"
        rx="18"
      />
      <line
        x1="260"
        y1="22"
        x2="260"
        y2="198"
      />
      <circle
        cx="260"
        cy="110"
        r="34"
      />

      <rect
        x="35"
        y="65"
        width="72"
        height="90"
      />
      <rect
        x="413"
        y="65"
        width="72"
        height="90"
      />

      <rect
        x="35"
        y="87"
        width="28"
        height="46"
      />
      <rect
        x="457"
        y="87"
        width="28"
        height="46"
      />

      <circle
        cx="126"
        cy="110"
        r="3"
      />
      <circle
        cx="394"
        cy="110"
        r="3"
      />
    </svg>
  );
}

function TicketDetailsPanel({
  ticket,
  loading,
  error,
}) {
  if (loading) {
    return (
      <div className="ticket-details-panel ticket-details-loading">
        <div className="ticket-details-loader" />

        <div>
          <strong>Loading ticket details</strong>
          <p>Getting the full information for this ticket.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ticket-details-panel ticket-details-error">
        {error}
      </div>
    );
  }

  if (!ticket) {
    return null;
  }

  const facilities = getFacilityItems(
    ticket.facilities,
  );

  return (
    <div className="ticket-details-panel">
      <div className="ticket-details-heading">
        <div>
          <p className="ticket-selection-eyebrow">
            Ticket details
          </p>

          <h4>
            {ticket.ticket_class} Ticket
          </h4>

          <p>
            {ticket.home_team}
            <span> vs </span>
            {ticket.away_team}
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
            {formatPrice(ticket.price)}
          </strong>
        </div>

        <div className="ticket-detail-item">
          <span>Class</span>
          <strong>
            {ticket.ticket_class || "—"}
          </strong>
        </div>

        <div className="ticket-detail-item">
          <span>Section</span>
          <strong>
            {ticket.seat_section || "—"}
          </strong>
        </div>

        <div className="ticket-detail-item">
          <span>Row</span>
          <strong>
            {ticket.seat_row || "—"}
          </strong>
        </div>

        <div className="ticket-detail-item">
          <span>Seat</span>
          <strong>
            {ticket.seat_number || "—"}
          </strong>
        </div>

        <div className="ticket-detail-item">
          <span>Remaining capacity</span>
          <strong>
            {ticket.remaining_capacity ?? "—"}
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
          <span>Venue capacity</span>
          <strong>
            {ticket.venue_capacity ?? "—"}
          </strong>
        </div>
      </div>

      {facilities.length > 0 && (
        <div className="ticket-facilities">
          <span>Facilities</span>

          <div>
            {facilities.map((facility) => (
              <span
                className="ticket-facility-chip"
                key={facility}
              >
                {facility}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function TicketsPage() {
  const {
    sport: sportParam = "football",
  } = useParams();

  const sport =
    sportParam.toLowerCase();

  const sportConfig =
    SPORT_CONFIG[sport]
    || SPORT_CONFIG.football;

  const [filters, setFilters] =
    useState(EMPTY_FILTERS);

  const [
    appliedFilters,
    setAppliedFilters,
  ] = useState(EMPTY_FILTERS);

  const [tickets, setTickets] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [
    cityOptions,
    setCityOptions,
  ] = useState([]);

  const [
    venueOptions,
    setVenueOptions,
  ] = useState([]);

  const [
    loadingCities,
    setLoadingCities,
  ] = useState(false);

  const [
    loadingVenues,
    setLoadingVenues,
  ] = useState(false);

  const [
    filterOptionsError,
    setFilterOptionsError,
  ] = useState("");

  const [
    expandedMatchId,
    setExpandedMatchId,
  ] = useState(null);

  const [
    selectedTicketClass,
    setSelectedTicketClass,
  ] = useState("");

  const [
    selectedTicketId,
    setSelectedTicketId,
  ] = useState(null);

  const [
    ticketDetails,
    setTicketDetails,
  ] = useState(null);

  const [
    ticketDetailsLoading,
    setTicketDetailsLoading,
  ] = useState(false);

  const [
    ticketDetailsError,
    setTicketDetailsError,
  ] = useState("");

  const selectedCity = useMemo(() => {
    const cityValue =
      normalize(filters.city);

    if (!cityValue) {
      return "";
    }

    return (
      cityOptions.find(
        (city) =>
          normalize(city)
          === cityValue,
      ) || ""
    );
  }, [
    cityOptions,
    filters.city,
  ]);

  useEffect(() => {
    setFilters(EMPTY_FILTERS);
    setAppliedFilters(EMPTY_FILTERS);

    setVenueOptions([]);
    setFilterOptionsError("");
    setError("");

    setExpandedMatchId(null);
    setSelectedTicketClass("");
    setSelectedTicketId(null);
    setTicketDetails(null);
    setTicketDetailsError("");
  }, [sport]);

  useEffect(() => {
    const controller =
      new AbortController();

    async function loadCities() {
      setLoadingCities(true);
      setFilterOptionsError("");

      try {
        const data =
          await getTicketFilterOptions(
            {
              sport,
            },
            {
              signal:
                controller.signal,
            },
          );

        setCityOptions(
          data?.cities || [],
        );
      } catch (requestError) {
        if (
          requestError.name
          !== "AbortError"
        ) {
          setCityOptions([]);

          setFilterOptionsError(
            requestError.message
            || "Could not load city options.",
          );
        }
      } finally {
        if (
          !controller.signal.aborted
        ) {
          setLoadingCities(false);
        }
      }
    }

    loadCities();

    return () =>
      controller.abort();
  }, [sport]);

  useEffect(() => {
    if (!selectedCity) {
      setVenueOptions([]);
      setLoadingVenues(false);

      return undefined;
    }

    const controller =
      new AbortController();

    async function loadVenues() {
      setLoadingVenues(true);
      setFilterOptionsError("");

      try {
        const data =
          await getTicketFilterOptions(
            {
              sport,
              city: selectedCity,
            },
            {
              signal:
                controller.signal,
            },
          );

        setVenueOptions(
          data?.venues || [],
        );
      } catch (requestError) {
        if (
          requestError.name
          !== "AbortError"
        ) {
          setVenueOptions([]);

          setFilterOptionsError(
            requestError.message
            || "Could not load venue options.",
          );
        }
      } finally {
        if (
          !controller.signal.aborted
        ) {
          setLoadingVenues(false);
        }
      }
    }

    loadVenues();

    return () =>
      controller.abort();
  }, [
    sport,
    selectedCity,
  ]);

  useEffect(() => {
    const controller =
      new AbortController();

    async function loadTickets() {
      setLoading(true);
      setError("");

      try {
        const data =
          await searchTickets(
            {
              sport,
              ...appliedFilters,
            },
            {
              signal:
                controller.signal,
            },
          );

        setTickets(
          data?.tickets || [],
        );
      } catch (requestError) {
        if (
          requestError.name
          !== "AbortError"
        ) {
          setError(
            requestError.message
            || "Could not load tickets.",
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

    loadTickets();

    return () =>
      controller.abort();
  }, [
    sport,
    appliedFilters,
  ]);

  useEffect(() => {
    if (!selectedTicketId) {
      setTicketDetails(null);
      setTicketDetailsError("");
      setTicketDetailsLoading(false);

      return undefined;
    }

    const controller =
      new AbortController();

    async function loadTicketDetails() {
      setTicketDetailsLoading(true);
      setTicketDetailsError("");
      setTicketDetails(null);

      try {
        const data =
          await getTicketDetails(
            selectedTicketId,
            {
              signal:
                controller.signal,
            },
          );

        setTicketDetails(
          data?.ticket || null,
        );
      } catch (requestError) {
        if (
          requestError.name
          !== "AbortError"
        ) {
          setTicketDetailsError(
            requestError.message
            || "Could not load ticket details.",
          );
        }
      } finally {
        if (
          !controller.signal.aborted
        ) {
          setTicketDetailsLoading(false);
        }
      }
    }

    loadTicketDetails();

    return () =>
      controller.abort();
  }, [selectedTicketId]);

  const matches = useMemo(() => {
    const groupedMatches =
      new Map();

    for (const ticket of tickets) {
      const currentMatch =
        groupedMatches.get(
          ticket.match_id,
        );

      if (currentMatch) {
        currentMatch.tickets.push(
          ticket,
        );

        continue;
      }

      groupedMatches.set(
        ticket.match_id,
        {
          match_id:
            ticket.match_id,

          sport:
            ticket.sport,

          home_team:
            ticket.home_team,

          away_team:
            ticket.away_team,

          match_datetime:
            ticket.match_datetime,

          league:
            ticket.league,

          venue:
            ticket.venue,

          city:
            ticket.city,

          tickets: [
            ticket,
          ],
        },
      );
    }

    return Array.from(
      groupedMatches.values(),
    ).map((match) => {
      const prices =
        match.tickets
          .map((ticket) =>
            Number(ticket.price),
          )
          .filter(Number.isFinite);

      const classMap =
        new Map();

      for (
        const ticket
        of match.tickets
      ) {
        const classKey =
          normalize(
            ticket.ticket_class,
          );

        if (!classMap.has(classKey)) {
          classMap.set(
            classKey,
            [],
          );
        }

        classMap
          .get(classKey)
          .push(ticket);
      }

      const classSummaries =
        Array.from(
          classMap.entries(),
        )
          .map(
            ([
              classKey,
              classTickets,
            ]) => {
              const classPrices =
                classTickets
                  .map((ticket) =>
                    Number(
                      ticket.price,
                    ),
                  )
                  .filter(
                    Number.isFinite,
                  );

              const meta =
                getClassMeta(
                  classTickets[0]
                    ?.ticket_class,
                );

              return {
                key: classKey,
                label: meta.label,
                description:
                  meta.description,
                tickets:
                  classTickets,
                count:
                  classTickets.length,
                minPrice:
                  classPrices.length
                    ? Math.min(
                        ...classPrices,
                      )
                    : null,
                maxPrice:
                  classPrices.length
                    ? Math.max(
                        ...classPrices,
                      )
                    : null,
              };
            },
          )
          .sort((a, b) => {
            const aIndex =
              TICKET_CLASS_ORDER
                .indexOf(a.key);

            const bIndex =
              TICKET_CLASS_ORDER
                .indexOf(b.key);

            const safeA =
              aIndex === -1
                ? 999
                : aIndex;

            const safeB =
              bIndex === -1
                ? 999
                : bIndex;

            return safeA - safeB;
          });

      return {
        ...match,

        minPrice:
          prices.length
            ? Math.min(...prices)
            : null,

        classSummaries,
      };
    });
  }, [tickets]);

  function handleFilterChange(
    event,
  ) {
    const {
      name,
      value,
    } = event.target;

    setFilters((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function handleCityChange(
    value,
  ) {
    setFilters((current) => ({
      ...current,
      city: value,
      venue: "",
    }));

    setVenueOptions([]);
  }

  function handleVenueChange(
    value,
  ) {
    setFilters((current) => ({
      ...current,
      venue: value,
    }));
  }

  function resetTicketSelection() {
    setSelectedTicketClass("");
    setSelectedTicketId(null);
    setTicketDetails(null);
    setTicketDetailsError("");
  }

  function handleMatchToggle(
    matchId,
  ) {
    if (
      expandedMatchId === matchId
    ) {
      setExpandedMatchId(null);
      resetTicketSelection();

      return;
    }

    setExpandedMatchId(matchId);
    resetTicketSelection();
  }

  function handleClassSelect(
    ticketClass,
  ) {
    setSelectedTicketClass(
      ticketClass,
    );

    setSelectedTicketId(null);
    setTicketDetails(null);
    setTicketDetailsError("");
  }

  function handleTicketSelect(
    ticketId,
  ) {
    setSelectedTicketId(
      ticketId,
    );
  }

  function handleSubmit(
    event,
  ) {
    event.preventDefault();

    const exactCity =
      filters.city
        ? cityOptions.find(
            (city) =>
              normalize(city)
              === normalize(
                filters.city,
              ),
          )
        : "";

    if (
      filters.city
      && !exactCity
    ) {
      setError(
        "Please select a valid city from the suggestions.",
      );

      return;
    }

    const exactVenue =
      filters.venue
        ? venueOptions.find(
            (venue) =>
              normalize(venue)
              === normalize(
                filters.venue,
              ),
          )
        : "";

    if (
      filters.venue
      && !exactVenue
    ) {
      setError(
        "Please select a valid venue from the suggestions.",
      );

      return;
    }

    setError("");

    const cleanFilters = {
      ...filters,

      city:
        exactCity || "",

      venue:
        exactVenue || "",
    };

    setFilters(cleanFilters);
    setAppliedFilters(
      cleanFilters,
    );

    setExpandedMatchId(null);
    resetTicketSelection();
  }

  function handleReset() {
    setFilters(
      EMPTY_FILTERS,
    );

    setAppliedFilters(
      EMPTY_FILTERS,
    );

    setVenueOptions([]);
    setError("");

    setExpandedMatchId(null);
    resetTicketSelection();
  }

  return (
    <section className="tickets-page">
      <div
        className={`sport-hero sport-hero-${sport}`}
      >
        <div className="sport-hero-copy">
          <p className="sport-hero-kicker">
            TikiTicket ·{" "}
            {sportConfig.label}
          </p>

          <h1>
            {sportConfig.label}{" "}
            Tickets
          </h1>

          <p>
            {sportConfig.subtitle}
          </p>
        </div>

        <div className="sport-hero-visual">
          <SportArtwork
            sport={sport}
          />

          <span>
            {sportConfig.label}
          </span>
        </div>
      </div>

      <form
        className="ticket-filters"
        onSubmit={handleSubmit}
      >
        <div className="ticket-filter-grid">
          <label className="ticket-filter-field">
            <span>
              Team
            </span>

            <input
              type="text"
              name="team"
              value={
                filters.team
              }
              onChange={
                handleFilterChange
              }
              placeholder="Team name"
            />
          </label>

          <AutoCompleteInput
            label="City"
            value={
              filters.city
            }
            options={
              cityOptions
            }
            onChange={
              handleCityChange
            }
            placeholder="Type or choose a city..."
            loading={
              loadingCities
            }
          />

          <AutoCompleteInput
            label="Venue"
            value={
              filters.venue
            }
            options={
              venueOptions
            }
            onChange={
              handleVenueChange
            }
            placeholder={
              selectedCity
                ? "Type or choose a venue..."
                : "Select a city first"
            }
            disabled={
              !selectedCity
            }
            loading={
              loadingVenues
            }
          />

          <label className="ticket-filter-field">
            <span>
              Class
            </span>

            <select
              name="ticket_class"
              value={
                filters.ticket_class
              }
              onChange={
                handleFilterChange
              }
            >
              <option value="">
                All classes
              </option>

              <option value="regular">
                Regular
              </option>

              <option value="premium">
                Premium
              </option>

              <option value="vip">
                VIP
              </option>
            </select>
          </label>

          <label className="ticket-filter-field">
            <span>
              Date
            </span>

            <input
              type="date"
              name="date"
              value={
                filters.date
              }
              onChange={
                handleFilterChange
              }
            />
          </label>

          <label className="ticket-filter-field">
            <span>
              Min price
            </span>

            <input
              type="number"
              min="0"
              name="min_price"
              value={
                filters.min_price
              }
              onChange={
                handleFilterChange
              }
              placeholder="0"
            />
          </label>

          <label className="ticket-filter-field">
            <span>
              Max price
            </span>

            <input
              type="number"
              min="0"
              name="max_price"
              value={
                filters.max_price
              }
              onChange={
                handleFilterChange
              }
              placeholder="Any"
            />
          </label>

          <label className="ticket-filter-field">
            <span>
              Sort
            </span>

            <select
              name="sort"
              value={
                filters.sort
              }
              onChange={
                handleFilterChange
              }
            >
              <option value="date_asc">
                Soonest
              </option>

              <option value="date_desc">
                Latest
              </option>

              <option value="price_asc">
                Lowest price
              </option>

              <option value="price_desc">
                Highest price
              </option>
            </select>
          </label>

          {filterOptionsError && (
            <p className="form-error ticket-filter-error">
              {filterOptionsError}
            </p>
          )}
        </div>

        <div className="ticket-filter-actions">
          <button
            type="button"
            className="button button-secondary"
            onClick={
              handleReset
            }
          >
            Reset
          </button>

          <button
            type="submit"
            className="button"
          >
            Search tickets
          </button>
        </div>
      </form>

      <div className="ticket-results-heading">
        <div>
          <p className="eyebrow">
            Available matches
          </p>

          <h2>
            {loading
              ? "Searching..."
              : `${matches.length} matches found`}
          </h2>
        </div>

        {!loading
          && !error
          && matches.length > 0
          && (
            <p className="ticket-results-hint">
              Choose a match to see its ticket types.
            </p>
          )}
      </div>

      {error && (
        <div className="ticket-state ticket-state-error">
          {error}
        </div>
      )}

      {!loading
        && !error
        && matches.length === 0
        && (
          <div className="ticket-state">
            No matches found for these filters.
          </div>
        )}

      {!loading
        && !error
        && matches.length > 0
        && (
          <div className="ticket-match-list">
            {matches.map(
              (match) => {
                const isExpanded =
                  expandedMatchId
                  === match.match_id;

                const selectedClassSummary =
                  match.classSummaries.find(
                    (summary) =>
                      summary.key
                      === selectedTicketClass,
                  );

                const classTickets =
                  selectedClassSummary
                    ?.tickets || [];

                return (
                  <article
                    className={`ticket-match ${
                      isExpanded
                        ? "ticket-match-open"
                        : ""
                    }`}
                    key={
                      match.match_id
                    }
                  >
                    <button
                      type="button"
                      className="ticket-match-summary"
                      onClick={() =>
                        handleMatchToggle(
                          match.match_id,
                        )
                      }
                      aria-expanded={
                        isExpanded
                      }
                    >
                      <div className="ticket-match-accent">
                        <span>
                          {sportConfig.label.charAt(
                            0,
                          )}
                        </span>
                      </div>

                      <div className="ticket-match-copy">
                        <div className="ticket-match-topline">
                          <span>
                            {match.league
                              || sportConfig.label}
                          </span>

                          <span>
                            Match #{match.match_id}
                          </span>
                        </div>

                        <h3>
                          {match.home_team}

                          <span>
                            vs
                          </span>

                          {match.away_team}
                        </h3>

                        <div className="ticket-match-meta">
                          <span>
                            {formatMatchDate(
                              match.match_datetime,
                            )}
                          </span>

                          <span>
                            {match.venue}
                          </span>

                          <span>
                            {match.city}
                          </span>
                        </div>

                        <div className="ticket-match-badges">
                          {match.classSummaries.map(
                            (summary) => (
                              <span
                                key={
                                  summary.key
                                }
                              >
                                {
                                  summary.label
                                }
                              </span>
                            ),
                          )}
                        </div>
                      </div>

                      <div className="ticket-match-action">
                        <span>
                          From
                        </span>

                        <strong>
                          {formatPrice(
                            match.minPrice,
                          )}
                        </strong>

                        <small>
                          {
                            match
                              .classSummaries
                              .length
                          }{" "}
                          ticket types
                        </small>

                        <span
                          className={`ticket-match-chevron ${
                            isExpanded
                              ? "open"
                              : ""
                          }`}
                          aria-hidden="true"
                        >
                          ↓
                        </span>
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="ticket-selection-panel">
                        <div className="ticket-selection-steps">
                          <div
                            className="ticket-selection-step active"
                          >
                            <span>
                              1
                            </span>

                            <div>
                              <strong>
                                Ticket type
                              </strong>

                              <small>
                                Choose a class
                              </small>
                            </div>
                          </div>

                          <div
                            className={`ticket-selection-step ${
                              selectedTicketClass
                                ? "active"
                                : ""
                            }`}
                          >
                            <span>
                              2
                            </span>

                            <div>
                              <strong>
                                Ticket
                              </strong>

                              <small>
                                Choose an option
                              </small>
                            </div>
                          </div>

                          <div
                            className={`ticket-selection-step ${
                              selectedTicketId
                                ? "active"
                                : ""
                            }`}
                          >
                            <span>
                              3
                            </span>

                            <div>
                              <strong>
                                Details
                              </strong>

                              <small>
                                Review ticket
                              </small>
                            </div>
                          </div>
                        </div>

                        <div className="ticket-selection-section">
                          <div className="ticket-selection-heading">
                            <div>
                              <p className="ticket-selection-eyebrow">
                                Step 1
                              </p>

                              <h4>
                                Choose your ticket type
                              </h4>
                            </div>

                            <p>
                              Only ticket types available for this match are shown.
                            </p>
                          </div>

                          <div className="ticket-type-grid">
                            {match.classSummaries.map(
                              (
                                summary,
                              ) => {
                                const isSelected =
                                  selectedTicketClass
                                  === summary.key;

                                return (
                                  <button
                                    type="button"
                                    className={`ticket-type-card ticket-type-${summary.key} ${
                                      isSelected
                                        ? "selected"
                                        : ""
                                    }`}
                                    key={
                                      summary.key
                                    }
                                    onClick={() =>
                                      handleClassSelect(
                                        summary.key,
                                      )
                                    }
                                  >
                                    <div className="ticket-type-card-top">
                                      <span className="ticket-type-name">
                                        {
                                          summary.label
                                        }
                                      </span>

                                      <span className="ticket-type-check">
                                        {isSelected
                                          ? "✓"
                                          : "→"}
                                      </span>
                                    </div>

                                    <p>
                                      {
                                        summary.description
                                      }
                                    </p>

                                    <div className="ticket-type-card-footer">
                                      <div>
                                        <span>
                                          From
                                        </span>

                                        <strong>
                                          {formatPrice(
                                            summary.minPrice,
                                          )}
                                        </strong>
                                      </div>

                                      <small>
                                        {
                                          summary.count
                                        }{" "}
                                        {summary.count
                                          === 1
                                          ? "ticket"
                                          : "tickets"}
                                      </small>
                                    </div>
                                  </button>
                                );
                              },
                            )}
                          </div>
                        </div>

                        {selectedClassSummary && (
                          <div className="ticket-selection-section ticket-options-section">
                            <div className="ticket-selection-heading">
                              <div>
                                <p className="ticket-selection-eyebrow">
                                  Step 2
                                </p>

                                <h4>
                                  {
                                    selectedClassSummary.label
                                  }{" "}
                                  tickets
                                </h4>
                              </div>

                              <p>
                                Choose one ticket to view its full details.
                              </p>
                            </div>

                            <div className="ticket-option-grid">
                              {classTickets.map(
                                (
                                  ticket,
                                  index,
                                ) => {
                                  const isSelected =
                                    selectedTicketId
                                    === ticket.id;

                                  return (
                                    <button
                                      type="button"
                                      className={`ticket-option-card ${
                                        isSelected
                                          ? "selected"
                                          : ""
                                      }`}
                                      key={
                                        ticket.id
                                      }
                                      onClick={() =>
                                        handleTicketSelect(
                                          ticket.id,
                                        )
                                      }
                                    >
                                      <div className="ticket-option-head">
                                        <span>
                                          Ticket{" "}
                                          #
                                          {
                                            ticket.id
                                          }
                                        </span>

                                        <span className="ticket-option-number">
                                          {String(
                                            index
                                            + 1,
                                          ).padStart(
                                            2,
                                            "0",
                                          )}
                                        </span>
                                      </div>

                                      <div className="ticket-option-seat">
                                        <span>
                                          {ticket.seat_section
                                            || "Seat details"}
                                        </span>

                                        <strong>
                                          {ticket.seat_row
                                            && ticket.seat_number
                                            ? `Row ${ticket.seat_row} · Seat ${ticket.seat_number}`
                                            : "Open to view"}
                                        </strong>
                                      </div>

                                      <div className="ticket-option-footer">
                                        <div>
                                          <span>
                                            Price
                                          </span>

                                          <strong>
                                            {formatPrice(
                                              ticket.price,
                                            )}
                                          </strong>
                                        </div>

                                        <div>
                                          <span>
                                            Available
                                          </span>

                                          <strong>
                                            {ticket.remaining_capacity
                                              ?? "—"}
                                          </strong>
                                        </div>
                                      </div>
                                    </button>
                                  );
                                },
                              )}
                            </div>
                          </div>
                        )}

                        {selectedTicketId && (
                          <div className="ticket-selection-section">
                            <div className="ticket-selection-heading">
                              <div>
                                <p className="ticket-selection-eyebrow">
                                  Step 3
                                </p>

                                <h4>
                                  Review ticket details
                                </h4>
                              </div>

                              <p>
                                Full information is loaded from the ticket details API.
                              </p>
                            </div>

                            <TicketDetailsPanel
                              ticket={
                                ticketDetails
                              }
                              loading={
                                ticketDetailsLoading
                              }
                              error={
                                ticketDetailsError
                              }
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </article>
                );
              },
            )}
          </div>
        )}
    </section>
  );
}