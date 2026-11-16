import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator

class ContributorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    is_verified: bool
    reputation_score: float
    account_age_days: int
    endorsements_count: int

class DestinationBase(BaseModel):
    name: str
    country: str
    region: str
    description: str
    category: str
    tags: List[str]
    rating: float
    review_count: int
    endorsement_count: int
    price_inr: int
    best_season: str
    image_url: str

class DestinationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str
    region: str
    description: str
    category: str
    tags: List[str]
    rating: float
    review_count: int
    endorsement_count: int
    price_inr: int
    best_season: str
    image_url: str
    created_at: Optional[datetime] = None

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [v] if v else []
        elif isinstance(v, list):
            return v
        return []

class PaginatedDestinations(BaseModel):
    items: List[DestinationOut]
    total: int
    page: int
    page_size: int
    pages: int

class ScoreBreakdown(BaseModel):
    final_score: float
    endorsement_score: float
    rating_score: float
    relevance_score: float

class RecommendationOut(DestinationOut):
    scores: ScoreBreakdown

class RecommendationsResponse(BaseModel):
    query: Optional[str] = None
    total: int
    results: List[RecommendationOut]

class SessionTokenOut(BaseModel):
    session_id: str
    contributor: Optional[ContributorOut] = None
    is_verified_session: bool
    issued_at: datetime

class EndorsementCreate(BaseModel):
    destination_id: int
    session_id: str
    contributor_id: Optional[int] = None

class EndorsementWithdraw(BaseModel):
    destination_id: int
    session_id: str

class EndorsementResponse(BaseModel):
    status: str
    destination_id: int
    new_count: int
    trust_weight: float = 1.0
    already_endorsed: bool = False

class DestinationEndorsementsOut(BaseModel):
    destination_id: int
    count: int
