from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.recommendation_engine import get_recommendations
from ..schemas.destination import RecommendationsResponse, RecommendationOut, DestinationOut, ScoreBreakdown

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("", response_model=RecommendationsResponse)
def recommend_destinations(
    q: Optional[str] = Query(None, description="Search keywords, travel vibe, or destination query"),
    region: Optional[str] = Query(None, description="Filter by region (India, Asia, Europe, South America, etc.)"),
    category: Optional[str] = Query(None, description="Filter by category (Beach, Nature, Luxury, Adventure, etc.)"),
    max_budget: Optional[int] = Query(None, ge=0, description="Maximum budget in INR"),
    limit: int = Query(12, ge=1, le=50, description="Max recommendations to return"),
    weight_endorsement: Optional[float] = Query(0.50, ge=0.0, le=1.0, description="Weight for trust-weighted endorsements"),
    weight_rating: Optional[float] = Query(0.30, ge=0.0, le=1.0, description="Weight for Bayesian-smoothed rating"),
    weight_relevance: Optional[float] = Query(0.20, ge=0.0, le=1.0, description="Weight for keyword query relevance"),
    db: Session = Depends(get_db),
):
    """
    Returns Stage 3 trust-aware, Bayesian-smoothed travel recommendations.
    Scoring: Configurable weights (default: 50% Endorsements + 30% Rating + 20% Relevance).
    Includes contributor trust weighting and temporal decay.
    Sorted descending by final recommendation score.
    """
    weights = {
        "endorsement": weight_endorsement,
        "rating": weight_rating,
        "relevance": weight_relevance,
    }

    raw_results = get_recommendations(
        db=db,
        query=q,
        region=region,
        category=category,
        max_budget=max_budget,
        limit=limit,
        weights=weights,
    )

    formatted_results = []
    for item in raw_results:
        dest = item["destination"]
        tags_list = item["tags"]
        scores_data = item["scores"]

        rec_out = RecommendationOut(
            id=dest.id,
            name=dest.name,
            country=dest.country,
            region=dest.region,
            description=dest.description,
            category=dest.category,
            tags=tags_list,
            rating=dest.rating,
            review_count=dest.review_count,
            endorsement_count=dest.endorsement_count,
            price_inr=dest.price_inr,
            best_season=dest.best_season,
            image_url=dest.image_url,
            latitude=dest.latitude,
            longitude=dest.longitude,
            source_name=dest.source_name,
            source_url=dest.source_url,
            source_license=dest.source_license,
            source_checked_at=dest.source_checked_at,
            created_at=dest.created_at,
            scores=ScoreBreakdown(**scores_data)
        )
        formatted_results.append(rec_out)

    return RecommendationsResponse(
        query=q,
        total=len(formatted_results),
        results=formatted_results,
    )
