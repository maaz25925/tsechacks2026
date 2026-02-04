from __future__ import annotations

"""
SQLAlchemy ORM models (declarative) matching Supabase tables.

We still use `supabase-py` for DB operations (PostgREST). These models are here for:
- Documentation / schema clarity
- Type hints
- Future: moving to direct SQLAlchemy + Postgres if desired
"""

from datetime import datetime
from typing import Any, Literal

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


Role = Literal["student", "teacher"]
ListingType = Literal["single_video", "multi_video_course"]
ListingStatus = Literal["draft", "published", "flagged"]
SessionStatus = Literal["pending", "active", "ended", "cancelled"]
PaymentType = Literal["lock", "settle", "refund"]
PaymentStatus = Literal["pending", "success", "failed"]


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String)
    role: Mapped[Role] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    bio: Mapped[str | None] = mapped_column(String, nullable=True)
    wallet_address: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    teacher_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[ListingType] = mapped_column(String)
    total_duration_min: Mapped[float] = mapped_column(Float)
    reserve_amount: Mapped[float] = mapped_column(Float)
    price_per_min: Mapped[float] = mapped_column(Float)
    tags: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[ListingStatus] = mapped_column(String)
    video_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # New fields for enhanced upload flow
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    visibility: Mapped[str | None] = mapped_column(String, nullable=True)  # "draft", "public", "private"
    base_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    transcription_url: Mapped[str | None] = mapped_column(String, nullable=True)
    course_outcomes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[str] = mapped_column(String)
    teacher_id: Mapped[str] = mapped_column(String)
    listing_id: Mapped[str] = mapped_column(String)
    status: Mapped[SessionStatus] = mapped_column(String)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    completion_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    engagement_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    final_amount_charged: Mapped[float | None] = mapped_column(Float, nullable=True)
    refund_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String)
    student_id: Mapped[str] = mapped_column(String)
    rating: Mapped[int] = mapped_column(Integer)
    review_text: Mapped[str] = mapped_column(String)
    credibility_score: Mapped[float] = mapped_column(Float)
    bonus_percentage: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String)
    type: Mapped[PaymentType] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[PaymentStatus] = mapped_column(String)
    finternet_tx_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

