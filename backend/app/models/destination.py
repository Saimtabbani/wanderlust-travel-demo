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
    created_at = Column(DateTime, default=datetime.utcnow)

    endorsements = relationship("Endorsement", back_populates="destination", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_dest_region_price", "region", "price_inr"),
        Index("idx_dest_category_price", "category", "price_inr"),
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
