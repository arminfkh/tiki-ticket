# Frontend foundation

This folder is a drop-in foundation for the existing Vite React project.

## Install the router

From the existing `frontend/` directory:

```bash
npm install react-router
```

## Copy the files

Replace the generated `src/` directory with this package's `src/` directory.
Replace the generated `vite.config.js` with this package's `vite.config.js`.

Copy `.env.example` to `.env` if you want an explicit local setting:

```bash
cp .env.example .env
```

The code also defaults to `/api`, so the `.env` file is optional for local development.

## Run

Start Django on port 8000, then from `frontend/`:

```bash
npm run dev
```

Vite proxies browser requests beginning with `/api` to `http://localhost:8000`,
so Django does not need a CORS change during local development.

## Current route ownership

Public:
- `/`
- `/login`
- `/signup`
- `/signup/verify`
- `/tickets`
- `/tickets/:ticketId`

Spectator:
- `/reservations`
- `/checkout/:reservationId`
- `/profile`
- `/bookings`
- `/report/:reservationId`

Support:
- `/support`

## Important backend contract notes

- API root is `/api/`.
- Authenticated requests use `Authorization: Bearer <access_token>`.
- Password login is `POST /api/auth/login/`.
- Signup is two-step: `POST /api/auth/signup/`, then `POST /api/auth/signup/verify/`.
- Search is `GET /api/tickets/`.
- Ticket filters supported by the backend:
  `sport`, `team`, `city`, `venue`, `ticket_class`, `date`,
  `min_price`, `max_price`, `sort`.
- `PATCH /api/profile/` exists, but there is currently no GET profile endpoint.
- Payment methods are `Card`, `Wallet`, and `Other`.
- For `Card` and `Other`, the current backend requires `simulate_result`.
