"""Account registration, login, logout, and session lookup endpoints."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.destination import Account, AuthSession, Contributor
from ..schemas.destination import AccountLogin, AccountPublic, AccountRegister, AuthSessionOut
from ..services.security import (
    default_session_expiry,
    generate_auth_token,
    hash_auth_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:].strip()
    return token or None


def get_optional_account(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> Optional[Account]:
    token = _bearer_token(authorization)
    if not token:
        return None
    session = db.query(AuthSession).filter(AuthSession.token_hash == hash_auth_token(token)).first()
    if not session or session.revoked_at or session.expires_at <= datetime.utcnow():
        return None
    return session.account


def _session_response(account: Account, db: Session) -> AuthSessionOut:
    raw_token = generate_auth_token()
    session = AuthSession(
        account_id=account.id,
        token_hash=hash_auth_token(raw_token),
        expires_at=default_session_expiry(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return AuthSessionOut(access_token=raw_token, expires_at=session.expires_at, account=account)


@router.post("/register", response_model=AuthSessionOut, status_code=status.HTTP_201_CREATED)
def register(payload: AccountRegister, db: Session = Depends(get_db)):
    if db.query(Account).filter(Account.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with that email already exists.")
    contributor = Contributor(
        username=f"member_{hash_auth_token(payload.email)[:12]}",
        display_name=payload.display_name,
        is_verified=False,
        reputation_score=0.5,
        account_age_days=0,
        endorsements_count=0,
    )
    db.add(contributor)
    db.flush()
    account = Account(
        email=payload.email,
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        contributor_id=contributor.id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return _session_response(account, db)


@router.post("/login", response_model=AuthSessionOut)
def login(payload: AccountLogin, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.email == payload.email.strip().lower()).first()
    if not account or not verify_password(payload.password, account.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")
    return _session_response(account, db)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    token = _bearer_token(authorization)
    if token:
        session = db.query(AuthSession).filter(AuthSession.token_hash == hash_auth_token(token)).first()
        if session and not session.revoked_at:
            session.revoked_at = datetime.utcnow()
            db.commit()
    return None


@router.get("/me", response_model=AccountPublic)
def me(account: Optional[Account] = Depends(get_optional_account)):
    if not account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to view this account.")
    return account
