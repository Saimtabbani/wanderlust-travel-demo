"""Private saved destinations and trip-plan endpoints for signed-in accounts."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models.destination import Account, Destination, Favorite, TripPlan, TripStop
from ..routes.auth import get_optional_account
from ..schemas.destination import FavoriteOut, TripPlanCreate, TripPlanOut

router = APIRouter(prefix="/traveller", tags=["traveller"])


def require_account(account: Account | None = Depends(get_optional_account)) -> Account:
    if not account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to manage saved destinations and trips.")
    return account


def _plan_out(plan: TripPlan) -> TripPlanOut:
    return TripPlanOut(
        id=plan.id,
        title=plan.title,
        notes=plan.notes,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        destinations=[stop.destination for stop in plan.stops],
    )


@router.get("/favorites", response_model=List[FavoriteOut])
def list_favorites(account: Account = Depends(require_account), db: Session = Depends(get_db)):
    return db.query(Favorite).options(joinedload(Favorite.destination)).filter(Favorite.account_id == account.id).order_by(Favorite.created_at.desc()).all()


@router.post("/favorites/{destination_id}", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def save_favorite(destination_id: int, account: Account = Depends(require_account), db: Session = Depends(get_db)):
    destination = db.get(Destination, destination_id)
    if not destination:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found.")
    favorite = db.query(Favorite).filter(Favorite.account_id == account.id, Favorite.destination_id == destination_id).first()
    if favorite:
        return favorite
    favorite = Favorite(account_id=account.id, destination_id=destination_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/favorites/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(destination_id: int, account: Account = Depends(require_account), db: Session = Depends(get_db)):
    favorite = db.query(Favorite).filter(Favorite.account_id == account.id, Favorite.destination_id == destination_id).first()
    if favorite:
        db.delete(favorite)
        db.commit()
    return None


@router.get("/trips", response_model=List[TripPlanOut])
def list_trips(account: Account = Depends(require_account), db: Session = Depends(get_db)):
    plans = db.query(TripPlan).options(joinedload(TripPlan.stops).joinedload(TripStop.destination)).filter(TripPlan.account_id == account.id).order_by(TripPlan.updated_at.desc()).all()
    return [_plan_out(plan) for plan in plans]


@router.post("/trips", response_model=TripPlanOut, status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripPlanCreate, account: Account = Depends(require_account), db: Session = Depends(get_db)):
    plan = TripPlan(account_id=account.id, title=payload.title, notes=payload.notes)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return _plan_out(plan)


@router.post("/trips/{trip_id}/destinations/{destination_id}", response_model=TripPlanOut)
def add_trip_destination(trip_id: int, destination_id: int, account: Account = Depends(require_account), db: Session = Depends(get_db)):
    plan = db.query(TripPlan).options(joinedload(TripPlan.stops).joinedload(TripStop.destination)).filter(TripPlan.id == trip_id, TripPlan.account_id == account.id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip plan not found.")
    if not db.get(Destination, destination_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found.")
    if not any(stop.destination_id == destination_id for stop in plan.stops):
        db.add(TripStop(trip_plan_id=plan.id, destination_id=destination_id, position=len(plan.stops)))
        db.commit()
        plan = db.query(TripPlan).options(joinedload(TripPlan.stops).joinedload(TripStop.destination)).filter(TripPlan.id == trip_id).first()
    return _plan_out(plan)


@router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, account: Account = Depends(require_account), db: Session = Depends(get_db)):
    plan = db.query(TripPlan).filter(TripPlan.id == trip_id, TripPlan.account_id == account.id).first()
    if plan:
        db.delete(plan)
        db.commit()
    return None
