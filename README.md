# Wanderlust

Wanderlust is a voice- and text-enabled travel discovery demo built as a final-year project. It lets visitors search destinations, apply region and budget filters, inspect an explainable recommendation score, and try a signed demo-session endorsement flow.

## What the demo demonstrates

- React + TypeScript travel discovery interface
- Browser voice input with a text-search fallback
- FastAPI recommendation API
- Transparent ranking from endorsement, rating, and keyword-relevance signals
- SQLite-backed demonstration catalogue
- Signed anonymous demo sessions to prevent simple duplicate endorsements

## Important prototype disclosure

The current catalogue, prices, ratings, and baseline endorsement counts are demonstration data. Wanderlust does **not** claim live traveller verification, current booking availability, real-time prices, or a production fraud-detection service.

Place identities and representative coordinates are now versioned with [Wikidata CC0 metadata](docs/DATA_PROVENANCE.md). Coordinate-based travel times are planning estimates, not live routes, schedules, fares, or safety advice.

## Run locally

Requirements: Node.js 20+ and Python 3.14.

```bash
npm install
py -m pip install -r backend/requirements.txt
```

Start the API in one terminal:

```bash
py -m uvicorn backend.app.main:app --port 8000 --reload
```

Start the web app in another terminal:

```bash
npm run dev
```

Open `http://localhost:5173`.

## Verification

```bash
npm run build
npm run lint
py -W ignore backend/test_backend.py
```

The backend test script currently exercises the data model, recommendation logic, signed session flow, duplicate prevention, withdrawal, and API endpoints.

For repeatable ranking checks, run `py backend/evaluate_recommendations.py`; read [the evaluation protocol](evaluation/README.md) before reporting any result.

## Deployment

This repository includes `vercel.json` for a single Vercel deployment containing the Vite frontend and FastAPI backend. In Vercel, configure:

| Variable | Required value |
| --- | --- |
| `WANDERLUST_SESSION_SECRET` | A new, long random value unique to the deployment |
| `WANDERLUST_DATABASE_URL` | Managed database URL before accepting real account or endorsement data |

Push the repository to GitHub, import it into Vercel, add the environment variable for Production and Preview, then deploy. The API is served at `/api`, so the frontend requires no separate public API URL.

The Vercel demo copies the seeded SQLite database to the function's temporary storage. Endorsements and locally registered accounts may reset when the function restarts. The app now has password-hashed, revocable bearer-token account sessions, but a public launch still requires a managed database (`WANDERLUST_DATABASE_URL`), email verification, distributed rate limiting, password reset, security monitoring, and privacy/retention controls.

## Project structure

```text
src/                   React frontend
backend/app/           FastAPI application and recommendation engine
backend/wanderlust.db  Seeded demonstration database
vercel.json            Full-stack Vercel routing
```
