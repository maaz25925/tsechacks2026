from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


Role = Literal["student", "teacher"]
ListingType = Literal["single_video", "multi_video_course"]
ListingStatus = Literal["draft", "published", "flagged"]
SessionStatus = Literal["pending", "active", "ended", "cancelled"]
PaymentType = Literal["lock", "settle", "refund"]
PaymentStatus = Literal["pending", "success", "failed"]


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "murph-backend"


class DiscoverySuggestRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class ListingPublic(BaseModel):
    id: str
    teacher_id: str
    title: str
    description: str | None = None
    type: ListingType
    total_duration_min: float
    reserve_amount: float
    price_per_min: float
    tags: dict[str, Any] | None = None
    thumbnail_url: str | None = None
    status: ListingStatus
    video_urls: list[str] | None = None


class DiscoverySuggestResponse(BaseModel):
    matches: list[ListingPublic]
    reasoning: str | None = None


class WalletConnectRequest(BaseModel):
    user_id: str


class WalletConnectResponse(BaseModel):
    wallet_address: str
    balance: float
    currency: str = "USD"


class WalletBalanceResponse(BaseModel):
    user_id: str
    wallet_address: str | None = None
    balance: float
    currency: str = "USD"


class SessionStartRequest(BaseModel):
    student_id: str
    listing_id: str
    # Optional override; otherwise uses listing.reserve_amount or default
    reserve_amount: float | None = None


class SessionStartResponse(BaseModel):
    session_id: str
    status: SessionStatus
    reserve_amount: float
    transaction_id: str


class SessionEndRequest(BaseModel):
    session_id: str
    # Frontend can send engagement data; backend computes final charge on end.
    completion_percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    engagement_metrics: dict[str, Any] | None = None


class SessionEndBreakdown(BaseModel):
    session_id: str
    listing_id: str
    teacher_id: str
    student_id: str
    start_time: datetime | None
    end_time: datetime | None
    duration_min: float
    completion_percentage: float
    reserve_amount: float
    final_amount_charged: float
    refund_amount: float
    settle_transaction_id: str
    refund_transaction_id: str


class ReviewSubmitRequest(BaseModel):
    session_id: str
    student_id: str
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(..., min_length=1, max_length=2000)


class ReviewSubmitResponse(BaseModel):
    review_id: str
    credibility_score: float = Field(..., ge=0.0, le=1.0)
    bonus_percentage: int = Field(..., ge=0, le=15)
    applied_bonus_amount: float


class CreatorUploadResponse(BaseModel):
    listing_id: str
    uploaded_url: str
    storage_path: str

