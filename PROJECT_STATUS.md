# Wanderlust — Mentor Demo Status

## Ready to demonstrate

- Voice and text destination search
- Region and budget filters
- Transparent score breakdowns
- FastAPI recommendation endpoints
- Signed anonymous demo-session endorsements
- GitHub/Vercel deployment configuration

## Demo boundaries

- The application uses seeded demonstration data (28 destinations, 5 sample contributors, and 7 sample relational endorsements).
- Prices, ratings, and endorsement totals are not live travel data.
- Voice recognition depends on browser support and microphone permission.
- Vercel deployments use temporary SQLite storage; endorsement changes are not durable.

## Before a real public beta

1. Add real authentication and contributor verification.
2. Replace SQLite with a managed persistent database.
3. Add rate limiting, moderation, privacy disclosures, and data-retention controls.
4. Collect consented, source-documented data and evaluate recommendation quality.
