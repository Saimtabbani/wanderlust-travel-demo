import math
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, or_
from ..models.destination import Destination, Endorsement, Contributor

STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or",
    "with", "is", "are", "trip", "travel", "place", "places", "visit", "destination", "destinations"
}

# ── Configurable Weights for Stage 3 ──
DEFAULT_WEIGHTS = {
    "endorsement": 0.50,
    "rating": 0.30,
    "relevance": 0.20,
}

# ── Contributor Trust Parameters ──
# Bounded [0.1, 1.0]. A neutral unauthenticated/new session receives the baseline 0.50.
TRUST_BASE_NEUTRAL = 0.50
TRUST_WEIGHT_VERIFIED = 0.25
TRUST_WEIGHT_AGE = 0.15      # Scaled up to 365 days
TRUST_WEIGHT_ACTIVITY = 0.10 # Scaled up to 20 contributions

# ── Temporal Decay Parameters ──
# Half-life = 180 days (6 months). Minimum retention floor = 0.40 (old endorsements retain >= 40% weight).
TEMPORAL_HALF_LIFE_DAYS = 180.0
TEMPORAL_DECAY_FLOOR = 0.40
TEMPORAL_LAMBDA = math.log(2) / TEMPORAL_HALF_LIFE_DAYS  # ~0.00385

def clean_tokens(text: str) -> List[str]:
    """Tokenize and filter common stop words."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
    return [w for w in words if len(w) > 1 and w not in STOPWORDS]

def calculate_contributor_trust(contributor: Optional[Contributor]) -> float:
    """
    Computes transparent contributor trust score T in [0.10, 1.00].
    When reliable contributor data is absent, returns neutral default (0.50).
    Does not claim verification proves physical travel experience.
    """
    if contributor is None:
        return TRUST_BASE_NEUTRAL

    trust = TRUST_BASE_NEUTRAL
    if contributor.is_verified:
        trust += TRUST_WEIGHT_VERIFIED

    # Account tenure factor (up to 1 year)
    age_factor = min(1.0, max(0.0, contributor.account_age_days / 365.0))
    trust += TRUST_WEIGHT_AGE * age_factor

    # Contribution volume factor (up to 20 valid endorsements)
    act_factor = min(1.0, max(0.0, contributor.endorsements_count / 20.0))
    trust += TRUST_WEIGHT_ACTIVITY * act_factor

    return round(min(1.0, max(0.10, trust)), 3)

def calculate_temporal_decay(created_at: Optional[datetime], now: Optional[datetime] = None) -> float:
    """
    Computes temporal decay factor in [TEMPORAL_DECAY_FLOOR, 1.0] using an exponential
    half-life of 180 days with a 40% floor so historical endorsements never evaporate.
    """
    if not created_at:
        return 1.0

    current_time = now or datetime.utcnow()
    delta_days = max(0.0, (current_time - created_at).total_seconds() / 86400.0)
    decay = TEMPORAL_DECAY_FLOOR + (1.0 - TEMPORAL_DECAY_FLOOR) * math.exp(-TEMPORAL_LAMBDA * delta_days)
    return round(min(1.0, max(TEMPORAL_DECAY_FLOOR, decay)), 3)

def compute_effective_endorsement_count(destination: Destination, now: Optional[datetime] = None) -> float:
    """
    Computes trust-weighted, temporally decayed endorsement count:
    Effective Count = baseline_demo_count + sum(Contributor_Trust_k * Temporal_Decay_k)
    """
    base_count = float(destination.baseline_endorsements or destination.endorsement_count or 0)

    # If relational endorsements exist, calculate their exact trust and temporal weights
    active_endorsements = destination.endorsements
    if not active_endorsements:
        return base_count

    relational_weight = 0.0
    for endr in active_endorsements:
        trust = calculate_contributor_trust(endr.contributor)
        decay = calculate_temporal_decay(endr.created_at, now)
        relational_weight += (trust * decay)

    # Reconcile baseline: baseline + trust-weighted real delta
    return base_count + relational_weight

def get_global_corpus_stats(db: Session):
    """
    Computes global destination corpus statistics across the entire database:
    - Global mean endorsement count (M_global)
    - Global max smoothed endorsement benchmark (Max_global)
    - Global mean rating (C_rating)
    Ensures that filtering candidates by region, category, or budget does NOT alter
    the destination's underlying Bayesian prior.
    """
    # Keep global priors database-side. Loading every destination here was
    # acceptable for the 28-place prototype, but becomes an N+1 query storm
    # with a real catalogue. Individual candidate endorsements are still
    # calculated exactly below; the global prior uses stored baseline values.
    base_endorsements = func.coalesce(
        Destination.baseline_endorsements,
        Destination.endorsement_count,
        0,
    )
    mean_endorsements, max_endorsements, mean_rating, count = db.query(
        func.avg(base_endorsements),
        func.max(base_endorsements),
        func.avg(Destination.rating),
        func.count(Destination.id),
    ).one()

    if not count:
        return {
            "mean_endorsements": 10000.0,
            "max_endorsements": 25000.0,
            "mean_rating": 4.7,
            "count": 0,
        }

    return {
        "mean_endorsements": float(mean_endorsements or 0.0),
        "max_endorsements": float(max_endorsements or 0.0),
        "mean_rating": float(mean_rating or 0.0),
        "count": int(count),
    }

def calculate_relevance(
    destination: Destination,
    tokens: List[str],
    tags_list: List[str]
) -> float:
    """
    Multi-field keyword relevance across name, country, region, category, tags, and description.
    """
    if not tokens:
        return 100.0  # Browsing baseline

    name_lower = destination.name.lower()
    country_lower = destination.country.lower()
    region_lower = destination.region.lower()
    category_lower = destination.category.lower()
    desc_lower = destination.description.lower()
    tags_lower = [t.lower() for t in tags_list]

    score = 0.0
    for token in tokens:
        if token == name_lower:
            score += 10.0
        elif token in name_lower:
            score += 6.0

        if token == country_lower:
            score += 8.0
        elif token in country_lower:
            score += 5.0

        if token == region_lower:
            score += 6.0
        elif token in region_lower:
            score += 4.0

        if token == category_lower or category_lower in token:
            score += 5.0

        for tag in tags_lower:
            if token == tag:
                score += 5.0
            elif token in tag:
                score += 3.0

        if token in desc_lower:
            score += 2.0

    return score

def get_recommendations(
    db: Session,
    query: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    max_budget: Optional[int] = None,
    limit: int = 12,
    weights: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """
    Stage 3 Trust-Aware Endorsement Recommendation Engine:
    - Global Bayesian Smoothing on Endorsements (corpus-wide prior, invariant to filters)
    - Sub-linear Bounded Logarithmic Scaling (no artificial bottom-zeroing, outlier dampening)
    - Contributor Trust & Temporal Weighting (effective counts)
    - Bayesian Smoothed Ratings
    - Multi-Field Relevance with query penalty
    """
    active_weights = {**DEFAULT_WEIGHTS, **(weights or {})}

    # 1. Compute global corpus statistics (global priors invariant to query filters)
    global_stats = get_global_corpus_stats(db)
    m_global = global_stats["mean_endorsements"]
    global_max = max(global_stats["max_endorsements"], 1000.0)
    c_rating_global = global_stats["mean_rating"]

    # 2. Filter candidates matching hard criteria
    stmt = db.query(Destination)

    if region and region.lower() != "all":
        stmt = stmt.filter(Destination.region.ilike(region))

    if category and category.lower() != "all":
        stmt = stmt.filter(Destination.category.ilike(category))

    if max_budget is not None and max_budget > 0:
        stmt = stmt.filter(Destination.price_inr <= max_budget)

    # A global catalogue can contain tens of thousands of records. Narrow
    # text searches before scoring instead of loading the entire table into a
    # serverless function. Browsing stays deterministic and is capped below.
    if query and query.strip():
        search_terms = clean_tokens(query)
        if search_terms:
            predicates = []
            for term in search_terms[:5]:
                match = f"%{term}%"
                predicates.extend([
                    Destination.name.ilike(match),
                    Destination.country.ilike(match),
                    Destination.category.ilike(match),
                    Destination.tags.ilike(match),
                ])
            stmt = stmt.filter(or_(*predicates))

    candidates: List[Destination] = stmt.options(
        selectinload(Destination.endorsements).selectinload(Endorsement.contributor)
    ).limit(1000).all()
    if not candidates:
        return []

    tokens = clean_tokens(query) if query else []
    now = datetime.utcnow()

    # Pre-calculate raw relevances for scaling
    raw_relevances = []
    tags_cache = []
    for d in candidates:
        tags = d.get_tags_list()
        tags_cache.append(tags)
        rel = calculate_relevance(d, tokens, tags)
        raw_relevances.append(rel)

    max_rel = max(raw_relevances) if raw_relevances else 0.0

    # 3. Calculate scores for each candidate
    scored_results = []
    c_smoothing = 10.0  # Bayesian prior confidence weight
    rating_prior_weight = 30.0  # Equivalent prior reviews

    for i, d in enumerate(candidates):
        # A. Trust-aware & temporally weighted effective endorsements
        eff_count = compute_effective_endorsement_count(d, now)

        # B. Global Bayesian Smoothing (Prior = M_global across entire database)
        smoothed_endorsement = (eff_count + (c_smoothing * m_global)) / (1.0 + c_smoothing)

        # C. Bounded Sub-linear Logarithmic Scaling (0 - 100)
        # Avoids candidate-subset distortion; lower counts receive reasonable base scores
        # Formula: 100 * ln(1 + smoothed) / ln(1 + global_max)
        log_smoothed = math.log(1.0 + max(0.0, smoothed_endorsement))
        log_benchmark = math.log(1.0 + global_max * 1.05)  # slight headroom
        endorsement_score = min(100.0, max(0.0, (log_smoothed / log_benchmark) * 100.0))

        # D. Bayesian Smoothed Rating (shrinkage towards global mean rating)
        rev_count = max(0, d.review_count)
        smoothed_rating = (
            (rev_count * d.rating) + (rating_prior_weight * c_rating_global)
        ) / (rev_count + rating_prior_weight)
        rating_score = min(100.0, max(0.0, (smoothed_rating / 5.0) * 100.0))

        # E. Relevance Score
        if not tokens:
            relevance_score = 100.0
        elif max_rel > 0:
            relevance_score = (raw_relevances[i] / max_rel) * 100.0 if raw_relevances[i] > 0 else 0.0
        else:
            relevance_score = 0.0
        relevance_score = min(100.0, max(0.0, relevance_score))

        # F. Weighted Final Score combining all 3 factors
        w_end = active_weights["endorsement"]
        w_rat = active_weights["rating"]
        w_rel = active_weights["relevance"]

        final_score = (w_end * endorsement_score) + (w_rat * rating_score) + (w_rel * relevance_score)

        # Penalty if search keywords were provided but destination has zero relevance
        if tokens and relevance_score == 0.0:
            final_score *= 0.20

        final_score = min(100.0, max(0.0, final_score))

        scored_results.append({
            "destination": d,
            "tags": tags_cache[i],
            "scores": {
                "final_score": round(final_score, 1),
                "endorsement_score": round(endorsement_score, 1),
                "rating_score": round(rating_score, 1),
                "relevance_score": round(relevance_score, 1),
            }
        })

    # 4. Sort descending by final score
    scored_results.sort(key=lambda x: x["scores"]["final_score"], reverse=True)

    # 5. Return top recommendations
    return scored_results[:limit]
