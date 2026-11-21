"""Controlled import of GeoNames' CC BY 4.0 populated-place catalogue."""
import csv
import io
import json
import zipfile
from datetime import date
from urllib.request import urlopen

from sqlalchemy.orm import Session

from ..models.destination import Destination

GEONAMES_CITIES_URL = "https://download.geonames.org/export/dump/cities5000.zip"
GEONAMES_COUNTRIES_URL = "https://download.geonames.org/export/dump/countryInfo.txt"
GEONAMES_LICENSE = "CC BY 4.0"


def _download(url: str) -> bytes:
    with urlopen(url, timeout=60) as response:  # nosec B310: fixed HTTPS source
        return response.read()


def _countries() -> dict:
    rows = _download(GEONAMES_COUNTRIES_URL).decode("utf-8").splitlines()
    countries = {}
    for row in csv.reader((line for line in rows if line and not line.startswith("#")), delimiter="\t"):
        if len(row) > 8:
            countries[row[0]] = {"name": row[4], "continent": row[8]}
    return countries


def import_geonames_cities(db: Session, limit: int = 50_000, batch_size: int = 500) -> dict:
    """Import up to 50k GeoNames cities; safe to repeat without duplicates."""
    countries = _countries()
    archive = zipfile.ZipFile(io.BytesIO(_download(GEONAMES_CITIES_URL)))
    filename = next(name for name in archive.namelist() if name.endswith(".txt"))
    imported = skipped = 0
    batch = []

    def flush(records):
        nonlocal imported, skipped
        if not records:
            return
        identifiers = [record["source_record_id"] for record in records]
        existing = {
            value for (value,) in db.query(Destination.source_record_id)
            .filter(Destination.source_record_id.in_(identifiers)).all()
        }
        insertable = [record for record in records if record["source_record_id"] not in existing]
        if insertable:
            db.bulk_insert_mappings(Destination, insertable)
            db.commit()
            imported += len(insertable)
        skipped += len(records) - len(insertable)

    with archive.open(filename) as raw:
        rows = csv.reader(io.TextIOWrapper(raw, encoding="utf-8"), delimiter="\t")
        for row in rows:
            if len(row) < 19 or row[6] != "P":
                continue
            geoname_id, name, ascii_name, _aliases, lat, lon, _class, feature_code, country_code, _cc2, _admin1, _admin2, _admin3, _admin4, population, _elevation, _dem, timezone, _modified = row[:19]
            country = countries.get(country_code, {"name": country_code, "continent": "World"})
            batch.append({
                "name": name or ascii_name,
                "country": country["name"],
                "region": country["continent"],
                "description": f"A populated place in {country['name']} recorded by GeoNames. Research local attractions, weather, entry rules, and transport before travel.",
                "category": "City",
                "tags": json.dumps(["City", feature_code, country["continent"]]),
                "rating": 0.0,
                "review_count": 0,
                "baseline_endorsements": 0,
                "endorsement_count": 0,
                "price_inr": 0,
                "best_season": "Research local climate",
                "image_url": "",
                "latitude": float(lat),
                "longitude": float(lon),
                "source_name": "GeoNames",
                "source_url": f"https://www.geonames.org/{geoname_id}",
                "source_license": GEONAMES_LICENSE,
                "source_checked_at": date.today().isoformat(),
                "source_record_id": f"geonames:{geoname_id}",
                "population": int(population or 0) or None,
                "timezone": timezone or None,
                "data_quality": "geographic_catalogue",
            })
            if len(batch) >= batch_size:
                flush(batch)
                batch = []
                if imported + skipped >= limit:
                    break
        if imported + skipped < limit:
            flush(batch)
    return {"source": "GeoNames cities5000", "license": GEONAMES_LICENSE, "imported": imported, "skipped": skipped}
