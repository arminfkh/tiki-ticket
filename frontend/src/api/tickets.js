import {
  ApiError,
  apiRequest,
} from "./client.js";


function normalizeAvailability(ticket) {
  const availabilityStatus =
    ticket.availability_status ??
    ticket.status ??
    null;

  const statusAvailable =
    typeof availabilityStatus === "string"
      ? availabilityStatus.toLowerCase() === "available"
      : null;

  const isSelectable =
    ticket.is_selectable ??
    ticket.is_available ??
    statusAvailable ??
    true;

  const isAvailable =
    ticket.is_available ??
    ticket.is_selectable ??
    statusAvailable ??
    true;

  return {
    is_selectable: Boolean(isSelectable),
    is_available: Boolean(isAvailable),

    availability_status:
      availabilityStatus ||
      (isAvailable ? "Available" : "Unavailable"),
  };
}


function normalizeTicket(ticket) {
  if (
    !ticket ||
    typeof ticket !== "object" ||
    Array.isArray(ticket)
  ) {
    return null;
  }

  const id =
    ticket.id ??
    ticket.ticket_id ??
    null;

  const matchId =
    ticket.match_id ??
    ticket.matchId ??
    null;

  return {
    ...ticket,

    id,

    ticket_id:
      ticket.ticket_id ??
      id,

    match_id: matchId,

    ...normalizeAvailability(ticket),
  };
}


function extractTickets(data) {
  const candidates = [
    data?.tickets,
    data?.results,
    data?.data?.tickets,

    Array.isArray(data)
      ? data
      : null,
  ];

  const rawTickets =
    candidates.find(Array.isArray);

  if (!rawTickets) {
    throw new ApiError(
      "The ticket search returned an unexpected response.",
      {
        code: "invalid_ticket_search_response",
      },
    );
  }

  return rawTickets
    .map(normalizeTicket)
    .filter(Boolean);
}


export async function searchTickets(
  filters = {},
  { signal } = {},
) {
  const params =
    new URLSearchParams();

  const allowedFilters = [
    "sport",
    "team",
    "city",
    "venue",
    "ticket_class",
    "date",
    "min_price",
    "max_price",
    "sort",
  ];

  for (const key of allowedFilters) {
    const value =
      filters[key];

    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      params.set(
        key,
        value,
      );
    }
  }

  const queryString =
    params.toString();

  const endpoint =
    queryString
      ? `/tickets/?${queryString}`
      : "/tickets/";

  const data =
    await apiRequest(
      endpoint,
      { signal },
    );

  return {
    ...(
      data &&
      typeof data === "object" &&
      !Array.isArray(data)
        ? data
        : {}
    ),

    tickets:
      extractTickets(data),
  };
}


export async function getTicketDetails(
  ticketId,
  { signal } = {},
) {
  const data =
    await apiRequest(
      `/tickets/${ticketId}/`,
      { signal },
    );

  const rawTicket =
    data?.ticket ??
    data?.data?.ticket ??
    (
      data &&
      typeof data === "object" &&
      !Array.isArray(data) &&
      (
        data.id !== undefined ||
        data.ticket_id !== undefined
      )
        ? data
        : null
    );

  const ticket =
    normalizeTicket(rawTicket);

  if (
    !ticket ||
    ticket.id === null ||
    ticket.id === undefined
  ) {
    throw new ApiError(
      "The ticket details endpoint returned an unexpected response.",
      {
        code: "invalid_ticket_details_response",
      },
    );
  }

  return {
    ...(
      data &&
      typeof data === "object" &&
      !Array.isArray(data)
        ? data
        : {}
    ),

    ticket,
  };
}


export async function getTicketFilterOptions(
  filters = {},
  { signal } = {},
) {
  const params =
    new URLSearchParams();

  if (filters.sport) {
    params.set(
      "sport",
      filters.sport,
    );
  }

  if (filters.city) {
    params.set(
      "city",
      filters.city,
    );
  }

  const queryString =
    params.toString();

  const endpoint =
    queryString
      ? `/tickets/filter-options/?${queryString}`
      : "/tickets/filter-options/";

  const data =
    await apiRequest(
      endpoint,
      { signal },
    );

  const optionSource =
    data?.filter_options ??
    data?.filters ??
    data?.data ??
    data;

  if (
    !optionSource ||
    typeof optionSource !== "object"
  ) {
    throw new ApiError(
      "The ticket filter endpoint returned an unexpected response.",
      {
        code: "invalid_ticket_filter_response",
      },
    );
  }

  return {
    ...data,

    cities:
      Array.isArray(optionSource.cities)
        ? optionSource.cities
        : [],

    venues:
      Array.isArray(optionSource.venues)
        ? optionSource.venues
        : [],
  };
}