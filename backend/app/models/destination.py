import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey,
    UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from ..database import Base

class Contributor(Base):
    """
    Represents an authenticated or identified community member who contributes endorsements.
    Tracks objective credibility indicators without claiming proof of physical experience.
    """
    __tablename__ = "contributors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    reputation_score = Column(Float, nullable=False, default=0.5)  # Bounded [0.1, 1.0], default neutral
    account_age_days = Column(Integer, nullable=False, default=0)
    endorsements_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    endorsements = relationship("Endorsement", back_populates="contributor", cascade="all, delete-orphan")


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    region = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    tags = Column(Text, nullable=False, default="[]")  # Stored as JSON string
    rating = Column(Float, nullable=False, default=4.5)  # Demo data rating
    review_count = Column(Integer, nullable=False, default=0)
    baseline_endorsements = Column(Integer, nullable=False, default=0)  # Seed demonstration baseline
    endorsement_count = Column(Integer, nullable=False, default=0, index=True)  # Total active endorsements
    price_inr = Column(Integer, nullable=False, index=True)
    best_season = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=False)
    # Geographic and provenance fields are deliberately separate from the
    # editorial/demo ranking signals above.  They make it possible to show a
    # reproducible distance estimate and to audit where each place record came
    # from without implying that ratings, prices, or endorsements are live.
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source_name = Column(String(100), nullable=True)
    source_url = Column(String(500), nullable=True)
    source_license = Column(String(100), nullable=True)
    source_checked_at = Column(String(20), nullable=True)
    source_record_id = Column(String(80), unique=True, nullable=True, index=True)
    population = Column(Integer, nullable=True, index=True)
    timezone = Column(String(64), nullable=True)
    data_quality = Column(String(32), nullable=False, default="prototype", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    endorsements = relationship("Endorsement", back_populates="destination", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_dest_region_price", "region", "price_inr"),
        Index("idx_dest_category_price", "category", "price_inr"),
        Index("idx_dest_name_country", "name", "country"),
    )

    def get_tags_list(self):
        """Helper to get deserialized list of tags."""
        try:
            return json.loads(self.tags) if self.tags else []
        except Exception:
            return []


class Endorsement(Base):
    __tablename__ = "endorsements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True)
    contributor_id = Column(Integer, ForeignKey("contributors.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(128), nullable=False, index=True)
    trust_weight = Column(Float, nullable=False, default=1.0)  # Calculated trust factor at time of endorsement
    is_verified_visit = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    destination = relationship("Destination", back_populates="endorsements")
    contributor = relationship("Contributor", back_populates="endorsements")

    __table_args__ = (
        # Ensure a session can endorse a destination only once
        UniqueConstraint("destination_id", "session_id", name="uq_destination_session"),
    )


class Account(Base):
    """A local account with a password hash and an optional contributor profile.

    This supports a deployable authentication boundary, but it still requires a
    managed database, email verification, and a distributed rate limiter before
    it is suitable for a public launch.
    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(254), unique=True, nullable=False, index=True)
    display_name = Column(String(80), nullable=False)
    password_hash = Column(String(256), nullable=False)
    contributor_id = Column(Integer, ForeignKey("contributors.id", ondelete="SET NULL"), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    contributor = relationship("Contributor")
    sessions = relationship("AuthSession", back_populates="account", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="account", cascade="all, delete-orphan")
    trip_plans = relationship("TripPlan", back_populates="account", cascade="all, delete-orphan")


class AuthSession(Base):
    """Hashed, revocable bearer-token session. Raw tokens are never stored."""
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship("Account", back_populates="sessions")


class Favorite(Base):
    """A durable saved destination belonging to a signed-in traveller."""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship("Account", back_populates="favorites")
    destination = relationship("Destination")

    __table_args__ = (UniqueConstraint("account_id", "destination_id", name="uq_favorite_account_destination"),)


class TripPlan(Base):
    """A private, named collection of destinations for a traveller."""
    __tablename__ = "trip_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    notes = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    account = relationship("Account", back_populates="trip_plans")
    stops = relationship("TripStop", back_populates="trip_plan", cascade="all, delete-orphan", order_by="TripStop.position")


class TripStop(Base):
    """An ordered destination inside a traveller's private trip plan."""
    __tablename__ = "trip_stops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_plan_id = Column(Integer, ForeignKey("trip_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    trip_plan = relationship("TripPlan", back_populates="stops")
    destination = relationship("Destination")

    __table_args__ = (UniqueConstraint("trip_plan_id", "destination_id", name="uq_trip_plan_destination"),)
