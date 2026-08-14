import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router";

import {
  getTicketFilterOptions,
  searchTickets,
} from "../api/tickets.js";

import AutocompleteInput from "../components/AutoCompleteInput.jsx";

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
  return value.trim().toLowerCase();
}

function SportArtwork({ sport }) {
  if (sport === "basketball") {
    return (
      <svg
        className="sport-hero-art"
        viewBox="0 0 520 220"
        aria-hidden="true"
      >
        <rect x="35" y="22" width="450" height="176" rx="18" />
        <line x1="260" y1="22" x2="260" y2="198" />
        <circle cx="260" cy="110" r="34" />

        <path d="M35 65h58v90H35M485 65h-58v90h58" />

        <path d="M93 84a52 52 0 0 1 0 52M427 84a52 52 0 0 0 0 52" />

        <circle cx="260" cy="110" r="82" />
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
        <rect x="35" y="35" width="450" height="150" rx="14" />

        <line x1="260" y1="35" x2="260" y2="185" />
        <line x1="210" y1="35" x2="210" y2="185" />
        <line x1="310" y1="35" x2="310" y2="185" />
        <line x1="35" y1="110" x2="485" y2="110" />

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
      <rect x="35" y="22" width="450" height="176" rx="18" />

      <line x1="260" y1="22" x2="260" y2="198" />

      <circle cx="260" cy="110" r="34" />

      <rect x="35" y="65" width="72" height="90" />
      <rect x="413" y="65" width="72" height="90" />

      <rect x="35" y="87" width="28" height="46" />
      <rect x="457" y="87" width="28" height="46" />

      <circle cx="126" cy="110" r="3" />
      <circle cx="394" cy="110" r="3" />
    </svg>
  );
}

function formatMatchDate(value) {
  if (!value) {
    return "Date unavailable";
  }

  const date = new Date(value);

  return new Intl.DateTimeFormat("en", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export default function TicketsPage() {
  const { sport: sportParam = "football" } = useParams();

  const sport = sportParam.toLowerCase();

  const sportConfig =
    SPORT_CONFIG[sport] || SPORT_CONFIG.football;

  const [filters, setFilters] = useState(EMPTY_FILTERS);

  const [appliedFilters, setAppliedFilters] =
    useState(EMPTY_FILTERS);

  const [tickets, setTickets] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  const [cityOptions, setCityOptions] = useState([]);

  const [venueOptions, setVenueOptions] = useState([]);

  const [loadingCities, setLoadingCities] = useState(false);

  const [loadingVenues, setLoadingVenues] = useState(false);

  const [filterOptionsError, setFilterOptionsError] =
    useState("");

  /*
   * City is considered selected only when the typed value
   * exactly matches one of the suggestions.
   */
  const selectedCity = useMemo(() => {
    const cityValue = normalize(filters.city);

    if (!cityValue) {
      return "";
    }

    return (
      cityOptions.find(
        (city) => normalize(city) === cityValue,
      ) || ""
    );
  }, [cityOptions, filters.city]);

  /*
   * Reset filters when sport changes.
   */
  useEffect(() => {
    setFilters(EMPTY_FILTERS);
    setAppliedFilters(EMPTY_FILTERS);
    setVenueOptions([]);
    setError("");
    setFilterOptionsError("");
  }, [sport]);

  /*
   * Load available cities for the selected sport.
   */
  useEffect(() => {
    const controller = new AbortController();

    async function loadCities() {
      setLoadingCities(true);
      setFilterOptionsError("");

      try {
        const data = await getTicketFilterOptions(
          {
            sport,
          },
          {
            signal: controller.signal,
          },
        );

        setCityOptions(data?.cities || []);
      } catch (requestError) {
        if (requestError.name !== "AbortError") {
          setCityOptions([]);

          setFilterOptionsError(
            requestError.message ||
              "Could not load city options.",
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoadingCities(false);
        }
      }
    }

    loadCities();

    return () => controller.abort();
  }, [sport]);

  /*
   * Load venues only when a valid city is selected.
   */
  useEffect(() => {
    if (!selectedCity) {
      setVenueOptions([]);
      setLoadingVenues(false);

      return undefined;
    }

    const controller = new AbortController();

    async function loadVenues() {
      setLoadingVenues(true);
      setFilterOptionsError("");

      try {
        const data = await getTicketFilterOptions(
          {
            sport,
            city: selectedCity,
          },
          {
            signal: controller.signal,
          },
        );

        setVenueOptions(data?.venues || []);
      } catch (requestError) {
        if (requestError.name !== "AbortError") {
          setVenueOptions([]);

          setFilterOptionsError(
            requestError.message ||
              "Could not load venue options.",
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoadingVenues(false);
        }
      }
    }

    loadVenues();

    return () => controller.abort();
  }, [sport, selectedCity]);

  /*
   * Search tickets using the filters that were submitted.
   */
  useEffect(() => {
    const controller = new AbortController();

    async function loadTickets() {
      setLoading(true);
      setError("");

      try {
        const data = await searchTickets(
          {
            sport,
            ...appliedFilters,
          },
          {
            signal: controller.signal,
          },
        );

        setTickets(data?.tickets || []);
      } catch (requestError) {
        if (requestError.name !== "AbortError") {
          setError(
            requestError.message ||
              "Could not load tickets.",
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadTickets();

    return () => controller.abort();
  }, [sport, appliedFilters]);

  /*
   * Group ticket records by match.
   */
  const matches = useMemo(() => {
    const groupedMatches = new Map();

    for (const ticket of tickets) {
      const currentMatch = groupedMatches.get(
        ticket.match_id,
      );

      if (currentMatch) {
        currentMatch.tickets.push(ticket);
        continue;
      }

      groupedMatches.set(ticket.match_id, {
        match_id: ticket.match_id,
        sport: ticket.sport,
        home_team: ticket.home_team,
        away_team: ticket.away_team,
        match_datetime: ticket.match_datetime,
        league: ticket.league,
        venue: ticket.venue,
        city: ticket.city,
        tickets: [ticket],
      });
    }

    return Array.from(groupedMatches.values()).map(
      (match) => {
        const prices = match.tickets.map((ticket) =>
          Number(ticket.price),
        );

        const classes = [
          ...new Set(
            match.tickets.map(
              (ticket) => ticket.ticket_class,
            ),
          ),
        ];

        return {
          ...match,
          minPrice: Math.min(...prices),
          classes,
        };
      },
    );
  }, [tickets]);

  function handleFilterChange(event) {
    const { name, value } = event.target;

    setFilters((current) => ({
      ...current,
      [name]: value,
    }));
  }

  /*
   * Changing city always clears the previously selected venue.
   */
  function handleCityChange(value) {
    setFilters((current) => ({
      ...current,
      city: value,
      venue: "",
    }));

    setVenueOptions([]);
  }

  function handleVenueChange(value) {
    setFilters((current) => ({
      ...current,
      venue: value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    /*
     * If City contains something, make sure it is
     * one of the available options.
     */
    const exactCity = filters.city
      ? cityOptions.find(
          (city) =>
            normalize(city) === normalize(filters.city),
        )
      : "";

    if (filters.city && !exactCity) {
      setError(
        "Please select a valid city from the suggestions.",
      );

      return;
    }

    /*
     * Same validation for Venue.
     */
    const exactVenue = filters.venue
      ? venueOptions.find(
          (venue) =>
            normalize(venue) === normalize(filters.venue),
        )
      : "";

    if (filters.venue && !exactVenue) {
      setError(
        "Please select a valid venue from the suggestions.",
      );

      return;
    }

    setError("");

    const cleanFilters = {
      ...filters,
      city: exactCity || "",
      venue: exactVenue || "",
    };

    setFilters(cleanFilters);

    setAppliedFilters(cleanFilters);
  }

  function handleReset() {
    setFilters(EMPTY_FILTERS);
    setAppliedFilters(EMPTY_FILTERS);

    setVenueOptions([]);

    setError("");
  }

  return (
    <section className="tickets-page">
      <div
        className={`sport-hero sport-hero-${sport}`}
      >
        <div className="sport-hero-copy">
          <p className="sport-hero-kicker">
            TikiTicket · {sportConfig.label}
          </p>

          <h1>
            {sportConfig.label} Tickets
          </h1>

          <p>
            {sportConfig.subtitle}
          </p>
        </div>

        <div className="sport-hero-visual">
          <SportArtwork sport={sport} />

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
          {/* TEAM */}

          <label className="ticket-filter-field">
            <span>Team</span>

            <input
              type="text"
              name="team"
              value={filters.team}
              onChange={handleFilterChange}
              placeholder="Team name"
            />
          </label>

          {/* CITY */}

          <AutocompleteInput
            label="City"
            value={filters.city}
            options={cityOptions}
            onChange={handleCityChange}
            placeholder="Type or choose a city..."
            loading={loadingCities}
          />

          {/* VENUE */}

          <AutocompleteInput
            label="Venue"
            value={filters.venue}
            options={venueOptions}
            onChange={handleVenueChange}
            placeholder={
              selectedCity
                ? "Type or choose a venue..."
                : "Select a city first"
            }
            disabled={!selectedCity}
            loading={loadingVenues}
          />

          {/* CLASS */}

          <label className="ticket-filter-field">
            <span>Class</span>

            <select
              name="ticket_class"
              value={filters.ticket_class}
              onChange={handleFilterChange}
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

          {/* DATE */}

          <label className="ticket-filter-field">
            <span>Date</span>

            <input
              type="date"
              name="date"
              value={filters.date}
              onChange={handleFilterChange}
            />
          </label>

          {/* MIN PRICE */}

          <label className="ticket-filter-field">
            <span>Min price</span>

            <input
              type="number"
              min="0"
              name="min_price"
              value={filters.min_price}
              onChange={handleFilterChange}
              placeholder="0"
            />
          </label>

          {/* MAX PRICE */}

          <label className="ticket-filter-field">
            <span>Max price</span>

            <input
              type="number"
              min="0"
              name="max_price"
              value={filters.max_price}
              onChange={handleFilterChange}
              placeholder="Any"
            />
          </label>

          {/* SORT */}

          <label className="ticket-filter-field">
            <span>Sort</span>

            <select
              name="sort"
              value={filters.sort}
              onChange={handleFilterChange}
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
            <p className="form-error">
              {filterOptionsError}
            </p>
          )}
        </div>

        <div className="ticket-filter-actions">
          <button
            type="button"
            className="button button-secondary"
            onClick={handleReset}
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
      </div>

      {error && (
        <div className="ticket-state ticket-state-error">
          {error}
        </div>
      )}

      {!loading &&
        !error &&
        matches.length === 0 && (
          <div className="ticket-state">
            No matches found for these filters.
          </div>
        )}

      {!loading &&
        !error &&
        matches.length > 0 && (
          <div className="match-list">
            {matches.map((match) => (
              <article
                className="match-ticket-card"
                key={match.match_id}
              >
                <div className="match-ticket-notch match-ticket-notch-left" />

                <div className="match-ticket-notch match-ticket-notch-right" />

                <div className="match-ticket-main">
                  <p className="match-ticket-league">
                    {match.league || sportConfig.label}
                  </p>

                  <h3>
                    {match.home_team}

                    <span>vs</span>

                    {match.away_team}
                  </h3>

                  <div className="match-ticket-meta">
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

                  <div className="match-ticket-classes">
                    {match.classes.map(
                      (ticketClass) => (
                        <span key={ticketClass}>
                          {ticketClass}
                        </span>
                      ),
                    )}
                  </div>
                </div>

                <div className="match-ticket-price">
                  <span>From</span>

                  <strong>
                    {match.minPrice.toFixed(2)}
                  </strong>

                  <small>
                    {match.tickets.length} ticket options
                  </small>
                </div>
              </article>
            ))}
          </div>
        )}
    </section>
  );
}