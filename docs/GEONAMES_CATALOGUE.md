# GeoNames global catalogue

Wanderlust imports the `cities5000.zip` GeoNames extract: approximately 50,000 populated places and administrative seats worldwide. GeoNames publishes this data under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), requiring visible attribution and a link to the licence. The importer records the GeoNames record URL, source identifier, licence, coordinate, population, time zone, and import date for every row.

This is a large **geographic catalogue**, not a complete travel-inventory feed. GeoNames does not provide verified traveller ratings, current fares, accommodation availability, licensed photos, attraction opening hours, or safety advisories. The product labels those fields as unavailable until an appropriate licensed provider is connected.

## Controlled import

`POST /api/admin/catalog/import/geonames?limit=50000` is protected by `WANDERLUST_CATALOG_IMPORT_KEY`. It is an operational endpoint, not a user-facing feature. Imports are idempotent through the `geonames:<id>` source record identifier.

For the initial catalogue, run once with the managed secret after the production deployment. Future refreshes should be run as a supervised operation; do not run a data refresh during an ordinary user request.
