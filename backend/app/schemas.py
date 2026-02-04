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
MilestoneStatus = Literal["pending", "proof_submitted", "completed", "failed"]
EscrowStatus = Literal["active", "released", "failed"]


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "murph-backend"


class DiscoverySuggestRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class ListingPublic(BaseModel):
    id: str
    teacher_id: str
    teacher_name: str | None = None  # From users.name
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
    reviews_rating: float | None = None  # Average rating from reviews


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


class CourseDetailResponse(BaseModel):
    """
    Response schema for GET /discovery/listings/{listing_id}
    Returns course detail with reviews rating and all metadata.
    """
    title: str
    description: str
    category: str
    teacher_name: str | None = None  # From users.name
    video_url: str | list[str]  # Single URL or array for multiple videos
    thumbnail: str
    reviews_rating: float | None  # Average rating from reviews table
    course_outcomes: list[str] | None  # AI-generated learning outcomes
    transcription: str | None  # Transcription text content or URL
    base_price: float | None = None  # Base price of the course
    total_duration_min: int | None = None  # Total duration in minutes
    price_per_min: float | None = None  # Price per minute


# ============ User CRUD Schemas ============

class UserCreateRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    role: Role
    password: str = Field(..., min_length=6)
    bio: str | None = Field(default=None, max_length=1000)


class UserUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    bio: str | None = Field(default=None, max_length=1000)


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: Role
    bio: str | None = None
    wallet_address: str | None = None
    created_at: datetime | None = None


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int


# ============ Teacher CRUD Schemas ============

class TeacherProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    bio: str | None = None
    wallet_address: str | None = None
    total_sessions: int
    base_earned: float
    bonus_earned: float
    total_earned: float
    avg_rating: float | None = None
    avg_credibility: float | None = None
    created_at: datetime | None = None


class TeacherUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    bio: str | None = Field(default=None, max_length=1000)


# ============ Escrow & Milestone Schemas ============

class PaymentIntentRequest(BaseModel):
    amount: float = Field(..., gt=0.0)
    currency: str = Field(default="USD", min_length=1, max_length=10)
    description: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] | None = None


class EscrowResponse(BaseModel):
    id: str
    session_id: str
    finternet_intent_id: str
    total_amount: float
    locked_amount: float
    status: EscrowStatus
    created_at: datetime | None = None


class MilestoneCreateRequest(BaseModel):
    escrow_id: str
    session_id: str
    index: int = Field(..., ge=0)
    description: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=0.0)
    percentage: float = Field(..., ge=0.0, le=100.0)


class ProofSubmitRequest(BaseModel):
    video_url: str = Field(..., min_length=1, max_length=1000)
    notes: str | None = Field(default=None, max_length=500)


class MilestoneResponse(BaseModel):
    id: str
    escrow_id: str
    session_id: str
    index: int
    description: str
    amount: float
    percentage: float
    status: MilestoneStatus
    proof_data: dict[str, Any] | None = None
    created_at: datetime | None = None


class MilestoneListResponse(BaseModel):
    milestones: list[MilestoneResponse]
    total: int


class MilestoneCompleteResponse(BaseModel):
    milestone_id: str
    status: MilestoneStatus
    amount_released: float
    finternet_tx_id: str | None = None
