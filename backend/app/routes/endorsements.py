from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models.destination import Destination, Endorsement, Contributor
from ..schemas.destination import (
    EndorsementCreate,
    EndorsementWithdraw,
    EndorsementResponse,
    DestinationEndorsementsOut,
    SessionTokenOut,
    ContributorOut,
)
from ..services.security import generate_secure_session_id, verify_session_id
from ..services.recommendation_engine import calculate_contributor_trust

router = APIRouter(tags=["endorsements"])

@router.get("/session", response_model=SessionTokenOut)
def issue_session():
    """
    Issues an anonymous, cryptographically signed demo-session token.

    A username cannot be supplied here: the application has no authentication
    provider yet, so binding an arbitrary request to a contributor would allow
    impersonation. Signed demo sessions receive the neutral trust weight.
    """
    token = generate_secure_session_id()

    return SessionTokenOut(
        session_id=token,
        contributor=None,
        is_verified_session=True,
        issued_at=datetime.utcnow(),
    )

@router.get("/contributors", response_model=List[ContributorOut])
def list_contributors(db: Session = Depends(get_db)):
    """
    Returns verified and demonstration community contributors.
    """
    return db.query(Contributor).order_by(Contributor.reputation_score.desc()).all()

@router.post("/endorsements", response_model=EndorsementResponse, status_code=status.HTTP_201_CREATED)
def endorse_destination(payload: EndorsementCreate, db: Session = Depends(get_db)):
    """
    Records a trust-weighted community endorsement.
    Enforces HMAC session token validation and database-level duplicate prevention.
    """
    # 1. Verify session token integrity
    is_valid, token_cid = verify_session_id(payload.session_id)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security verification failed: Invalid or unsigned session token. Obtain a valid token from /api/session."
        )

    # 2. Check destination existence
    dest = db.query(Destination).filter(Destination.id == payload.destination_id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {payload.destination_id} not found."
        )

    # 3. Check for existing duplicate endorsement
    existing = db.query(Endorsement).filter(
        Endorsement.destination_id == payload.destination_id,
        Endorsement.session_id == payload.session_id.strip()
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already endorsed: This destination has already been endorsed by this session."
        )

    # 4. Determine contributor identity & server-calculated trust weight
    # Contributor identity can only come from a future authenticated token,
    # never from a client-controlled request body.
    cid = token_cid
    contributor = None
    if cid:
        contributor = db.query(Contributor).filter(Contributor.id == cid).first()

    trust_factor = calculate_contributor_trust(contributor)

    try:
        new_endorsement = Endorsement(
            destination_id=payload.destination_id,
            contributor_id=contributor.id if contributor else None,
            session_id=payload.session_id.strip(),
            trust_weight=trust_factor,
            is_verified_visit=bool(contributor and contributor.is_verified),
            created_at=datetime.utcnow(),
        )
        db.add(new_endorsement)

        # Atomic increment of destination count
        db.query(Destination).filter(Destination.id == payload.destination_id).update(
            {Destination.endorsement_count: Destination.endorsement_count + 1}
        )

        if contributor:
            db.query(Contributor).filter(Contributor.id == contributor.id).update(
                {Contributor.endorsements_count: Contributor.endorsements_count + 1}
            )

        db.commit()
        db.refresh(dest)

        return EndorsementResponse(
            status="success",
            destination_id=dest.id,
            new_count=dest.endorsement_count,
            trust_weight=trust_factor,
            already_endorsed=False,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already endorsed: Duplicate endorsement detected."
        )

@router.delete("/endorsements", response_model=EndorsementResponse)
def withdraw_endorsement(payload: EndorsementWithdraw, db: Session = Depends(get_db)):
    """
    Withdraws a previously recorded endorsement, safely decrementing the count
    and removing the relational record.
    """
    is_valid, _ = verify_session_id(payload.session_id)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unsigned session token."
        )

    dest = db.query(Destination).filter(Destination.id == payload.destination_id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {payload.destination_id} not found."
        )

    existing = db.query(Endorsement).filter(
        Endorsement.destination_id == payload.destination_id,
        Endorsement.session_id == payload.session_id.strip()
    ).first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active endorsement found for this destination and session."
        )

    contributor_id = existing.contributor_id

    # Remove endorsement
    db.delete(existing)

    # Atomic decrement of destination count (cannot drop below baseline)
    min_count = dest.baseline_endorsements or 0
    new_count = max(min_count, dest.endorsement_count - 1)
    db.query(Destination).filter(Destination.id == payload.destination_id).update(
        {Destination.endorsement_count: new_count}
    )

    if contributor_id:
        contrib = db.query(Contributor).filter(Contributor.id == contributor_id).first()
        if contrib and contrib.endorsements_count > 0:
            db.query(Contributor).filter(Contributor.id == contributor_id).update(
                {Contributor.endorsements_count: Contributor.endorsements_count - 1}
            )

    db.commit()
    db.refresh(dest)

    return EndorsementResponse(
        status="withdrawn",
        destination_id=dest.id,
        new_count=dest.endorsement_count,
        trust_weight=1.0,
        already_endorsed=False,
    )

@router.get("/destinations/{destination_id}/endorsements", response_model=DestinationEndorsementsOut)
def get_destination_endorsements(destination_id: int, db: Session = Depends(get_db)):
    """
    Retrieve real-time endorsement count for a destination.
    """
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found."
        )
    return DestinationEndorsementsOut(
        destination_id=dest.id,
        count=dest.endorsement_count,
    )
