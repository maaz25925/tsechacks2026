from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

from app.errors import http_error
from app.schemas import ReviewSubmitRequest, ReviewSubmitResponse
from app.services.ai import get_ai
from app.supabase_client import get_supabase, utc_now_iso

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/submit", response_model=ReviewSubmitResponse)
def submit(req: ReviewSubmitRequest) -> ReviewSubmitResponse:
    sb = get_supabase()

    session = sb.maybe_single("sessions", "*", id=req.session_id)
    if not session:
        raise http_error(404, "Session not found", code="SESSION_NOT_FOUND")
    if session.get("status") != "ended":
        raise http_error(400, "Session must be ended before review", code="SESSION_NOT_ENDED")
    if session.get("student_id") != req.student_id:
        raise http_error(403, "Not allowed to review this session", code="FORBIDDEN")

    duration_min = float(session.get("duration_min") or 0.0)
    completion = float(session.get("completion_percentage") or 0.0)
    engagement = session.get("engagement_metrics") or {}

    ai = get_ai()
    try:
        credibility, bonus_pct = ai.score_review_credibility(
            rating=req.rating,
            review_text=req.review_text,
            engagement_metrics=engagement,
            completion_percentage=completion,
            duration_min=duration_min,
        )
    except Exception:
        # If AI is unavailable, simple heuristic:
        credibility = 0.4 + (completion / 100.0) * 0.6
        credibility = max(0.0, min(1.0, credibility))
        bonus_pct = 0
        if req.rating >= 4 and credibility >= 0.75:
            bonus_pct = 10

    # Bonus applies on amount charged (as a teacher bonus, paid by platform in real life).
    final_amount = float(session.get("final_amount_charged") or 0.0)
    applied_bonus_amount = round(final_amount * (bonus_pct / 100.0), 2)

    review_id = f"rev_{uuid4().hex}"
    sb.insert(
        "reviews",
        {
            "id": review_id,
            "session_id": req.session_id,
            "student_id": req.student_id,
            "rating": req.rating,
            "review_text": req.review_text,
            "credibility_score": round(float(credibility), 3),
            "bonus_percentage": int(bonus_pct),
            "created_at": utc_now_iso(),
        },
    )

    return ReviewSubmitResponse(
        review_id=review_id,
        credibility_score=round(float(credibility), 3),
        bonus_percentage=int(bonus_pct),
        applied_bonus_amount=applied_bonus_amount,
    )

