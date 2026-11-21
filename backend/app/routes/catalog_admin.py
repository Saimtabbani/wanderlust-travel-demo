"""Restricted operational endpoint for one-time catalogue imports."""
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.geonames_importer import import_geonames_cities

router = APIRouter(prefix="/admin/catalog", tags=["catalog administration"])


def _authorised(key: str | None) -> bool:
    expected = os.getenv("WANDERLUST_CATALOG_IMPORT_KEY")
    return bool(expected and key and hmac.compare_digest(expected, key))


@router.post("/import/geonames")
def import_geonames(
    x_catalog_import_key: str | None = Header(None),
    limit: int = Query(50_000, ge=1, le=50_000),
    db: Session = Depends(get_db),
):
    """Import CC BY 4.0 populated-place data; not exposed to ordinary users."""
    if not _authorised(x_catalog_import_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Catalog import authorization is required.")
    try:
        return import_geonames_cities(db, limit=limit)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="GeoNames import did not complete.") from exc
