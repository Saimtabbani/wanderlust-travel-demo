import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from ..database import get_db
from ..models.destination import Destination
from ..schemas.destination import DestinationOut, PaginatedDestinations
from ..services.travel_estimates import flight_planning_estimate

router = APIRouter(prefix="/destinations", tags=["destinations"])

@router.get("", response_model=PaginatedDestinations)
def list_destinations(
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(12, ge=1, le=50, description="Items per page"),
    region: Optional[str] = Query(None, description="Filter by region (e.g. India, Asia, Europe, South America)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. Beach, Nature, Adventure)"),
    max_budget: Optional[int] = Query(None, ge=0, description="Maximum trip budget in INR"),
    sort_by: Optional[str] = Query("endorsements", description="Sort order: endorsements, rating, price_asc, price_desc"),
    db: Session = Depends(get_db),
):
    """
    List destinations with optional filtering, sorting and pagination.
    """
    query = db.query(Destination)

    # Filtering
    if region and region.lower() != "all":
        query = query.filter(Destination.region.ilike(region))

    if category and category.lower() != "all":
        query = query.filter(Destination.category.ilike(category))

    if max_budget is not None and max_budget > 0:
        query = query.filter(Destination.price_inr <= max_budget)

    # Sorting
    if sort_by == "rating":
        query = query.order_by(desc(Destination.rating), desc(Destination.endorsement_count))
    elif sort_by == "price_asc":
        query = query.order_by(asc(Destination.price_inr))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Destination.price_inr))
    else:  # default endorsements
        query = query.order_by(desc(Destination.endorsement_count), desc(Destination.rating))

    total = query.count()
    pages = math.ceil(total / page_size) if total > 0 else 1

    # Offset & limit
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedDestinations(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )

@router.get("/{destination_id}", response_model=DestinationOut)
def get_destination(destination_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single destination by its ID.
    """
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found."
        )
    return dest


@router.get("/{destination_id}/travel-estimate")
def get_travel_estimate(
    destination_id: int,
    origin_lat: float = Query(28.6139, ge=-90, le=90, description="Origin latitude; defaults to New Delhi"),
    origin_lon: float = Query(77.2090, ge=-180, le=180, description="Origin longitude; defaults to New Delhi"),
    db: Session = Depends(get_db),
):
    """Return a physically grounded planning estimate, not live transport data."""
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found.")
    estimate = flight_planning_estimate(origin_lat, origin_lon, dest.latitude, dest.longitude)
    if not estimate:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Coordinate data is unavailable for this destination.")
    return {"destination_id": dest.id, "origin": {"latitude": origin_lat, "longitude": origin_lon}, **estimate}
