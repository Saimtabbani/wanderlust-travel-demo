# Wanderlust Backend API

FastAPI + SQLite (SQLAlchemy) backend powering the Wanderlust endorsement-based travel recommendation engine.

## Features
- **SQLite Database** with `destinations` and `endorsements` tables, indexed on frequently queried columns.
- **Duplicate Endorsement Prevention** using a unique constraint on `(destination_id, session_id)`.
- **Endorsement-Based Recommendation Algorithm**:
  - 50% Bayesian-smoothed endorsement score
  - 30% Normalized rating score
  - 20% Multi-field keyword relevance score
- **REST Endpoints**:
  - `GET /api/health` — Service health & database destination count
  - `GET /api/destinations` — Paginated listing with region, category & budget filters
  - `GET /api/destinations/{id}` — Destination details
  - `GET /api/recommendations` — Scored and ranked recommendations with score breakdowns
  - `POST /api/endorsements` — Register session endorsement with duplicate prevention (HTTP 409)
  - `GET /api/destinations/{id}/endorsements` — Real-time endorsement count

## Running the Backend

From the project root:
```bash
py -m uvicorn backend.app.main:app --port 8000 --reload
```
Or from the `backend` folder:
```bash
cd backend
py -m uvicorn app.main:app --port 8000 --reload
```
API Documentation will be available at: http://localhost:8000/docs
