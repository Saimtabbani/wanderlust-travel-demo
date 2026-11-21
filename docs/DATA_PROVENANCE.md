# Destination catalogue provenance

Wanderlust v0.4 uses a **source-backed geographic catalogue** for its 28 destination identities and representative coordinates. The `backend/app/data/catalog_metadata.py` registry maps each displayed place to a Wikidata item and records the source URL, licence, and review date in the API response.

| Field | Source and licence | Meaning |
| --- | --- | --- |
| Place identity and representative coordinate | [Wikidata](https://www.wikidata.org/), [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Source-backed geographic metadata used in distance estimates. |
| Distance and flight-time estimate | Wanderlust calculation | Great-circle distance plus explicit planning assumptions; not routing or schedule data. |
| Descriptions, images, seasons, prices, ratings, reviews, and endorsements | Existing Wanderlust prototype data | Editorial or demonstration data; not asserted to be live, licensed supplier feeds, or verified traveller records. |

## Reproduction

The catalogue mapping is version-controlled in `backend/app/data/catalog_metadata.py`. On startup the application backfills provenance fields into the local prototype database. To reproduce the geometry calculation, call:

```text
GET /api/destinations/{id}/travel-estimate?origin_lat=28.6139&origin_lon=77.2090
```

The defaults are New Delhi coordinates. The result labels all assumptions and must not be used as a fare, booking, safety, emissions, or arrival-time claim.

## What remains before calling this a real travel dataset

This is a defensible **catalogue provenance foundation**, not a complete licensed travel-inventory integration. A publication or public beta needs a separate licensed provider/feed for current availability, prices, reviews, media rights, refresh schedules, and deletion/correction processes. Record each source version and retrieval date, retain its licence text, and comply with provider terms before adding those fields to evaluation or user-facing claims.
