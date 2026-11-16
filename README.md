# Wanderlust

Wanderlust is a voice- and text-enabled travel discovery demo built as a final-year project. It lets visitors search destinations, apply region and budget filters, inspect an explainable recommendation score, and try a signed demo-session endorsement flow.

## What the demo demonstrates

- React + TypeScript travel discovery interface
- Browser voice input with a text-search fallback
- FastAPI recommendation API
- Transparent ranking from endorsement, rating, and keyword-relevance signals
- SQLite-backed demonstration catalogue
- Signed anonymous demo sessions to prevent simple duplicate endorsements

## Important demo disclosure

The current catalogue, prices, ratings, and baseline endorsement counts are demonstration data. Wanderlust does **not** claim live traveller verification, current booking availability, real-time prices, or a production fraud-detection service.

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

## Deployment

This repository includes `vercel.json` for a single Vercel deployment containing the Vite frontend and FastAPI backend. In Vercel, configure:

| Variable | Required value |
| --- | --- |
| `WANDERLUST_SESSION_SECRET` | A new, long random value unique to the deployment |

Push the repository to GitHub, import it into Vercel, add the environment variable for Production and Preview, then deploy. The API is served at `/api`, so the frontend requires no separate public API URL.

The Vercel demo copies the seeded SQLite database to the function's temporary storage. Endorsements are therefore demonstration-only and may reset when the function restarts. Use a managed database and real authentication before accepting real user data.

## Project structure

```text
src/                   React frontend
backend/app/           FastAPI application and recommendation engine
backend/wanderlust.db  Seeded demonstration database
vercel.json            Full-stack Vercel routing
```
