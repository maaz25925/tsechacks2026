from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter

from app.errors import http_error
from app.schemas import TeacherProfileResponse, TeacherUpdateRequest
from app.supabase_client import get_supabase

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/profile/{teacher_id}", response_model=TeacherProfileResponse)
def get_teacher_profile(teacher_id: str) -> TeacherProfileResponse:
    """
    Get teacher profile with earnings and metrics.
    """
    sb = get_supabase()
    teacher = sb.maybe_single("users", "*", id=teacher_id)
    if not teacher or teacher.get("role") != "teacher":
        raise http_error(404, "Teacher not found", code="TEACHER_NOT_FOUND")

    sessions = (
        sb.client.table("sessions")
        .select("id,final_amount_charged")
        .eq("teacher_id", teacher_id)
        .eq("status", "ended")
        .execute()
        .data
        or []
    )
    session_amounts = {s["id"]: float(s.get("final_amount_charged") or 0.0) for s in sessions}

    total_sessions = len(sessions)
    base_earned = sum(session_amounts.values())
    bonus_earned = 0.0
    ratings = []
    cred_scores = []

    if sessions:
        session_ids = list(session_amounts.keys())
        reviews = (
            sb.client.table("reviews")
            .select("session_id,rating,credibility_score,bonus_percentage")
            .in_("session_id", session_ids)
            .execute()
            .data
            or []
        )

        for r in reviews:
            sid = r["session_id"]
            amount = session_amounts.get(sid, 0.0)
            bonus_pct = float(r.get("bonus_percentage") or 0.0)
            bonus_earned += amount * (bonus_pct / 100.0)
            ratings.append(float(r.get("rating") or 0.0))
            cred_scores.append(float(r.get("credibility_score") or 0.0))

    avg_rating = (sum(ratings) / len(ratings)) if ratings else None
    avg_cred = (sum(cred_scores) / len(cred_scores)) if cred_scores else None

    return TeacherProfileResponse(
        id=teacher["id"],
        email=teacher["email"],
        name=teacher["name"],
        bio=teacher.get("bio"),
        wallet_address=teacher.get("wallet_address"),
        total_sessions=total_sessions,
        base_earned=round(base_earned, 2),
        bonus_earned=round(bonus_earned, 2),
        total_earned=round(base_earned + bonus_earned, 2),
        avg_rating=round(avg_rating, 2) if avg_rating is not None else None,
        avg_credibility=round(avg_cred, 3) if avg_cred is not None else None,
        created_at=teacher.get("created_at"),
    )


@router.put("/{teacher_id}", response_model=TeacherProfileResponse)
def update_teacher_profile(teacher_id: str, req: TeacherUpdateRequest) -> TeacherProfileResponse:
    """
    Update teacher profile (name, bio).
    """
    sb = get_supabase()
    teacher = sb.maybe_single("users", "*", id=teacher_id)
    if not teacher or teacher.get("role") != "teacher":
        raise http_error(404, "Teacher not found", code="TEACHER_NOT_FOUND")

    update_data = {}
    if req.name is not None:
        update_data["name"] = req.name
    if req.bio is not None:
        update_data["bio"] = req.bio

    if update_data:
        try:
            sb.update("users", update_data, id=teacher_id)
        except Exception as e:
            raise http_error(400, f"Failed to update teacher: {str(e)}", code="UPDATE_FAILED")

    # Return updated profile
    return get_teacher_profile(teacher_id)


@router.get("/earnings/{teacher_id}")
def earnings(teacher_id: str) -> dict:
    """
    Aggregate base earnings + quality bonus for a teacher.
    """
    sb = get_supabase()
    teacher = sb.maybe_single("users", "*", id=teacher_id)
    if not teacher or teacher.get("role") != "teacher":
        raise http_error(404, "Teacher not found", code="TEACHER_NOT_FOUND")

    sessions = (
        sb.client.table("sessions")
        .select("id,final_amount_charged")
        .eq("teacher_id", teacher_id)
        .eq("status", "ended")
        .execute()
        .data
        or []
    )
    session_amounts = {s["id"]: float(s.get("final_amount_charged") or 0.0) for s in sessions}

    if not sessions:
        return {
            "teacher_id": teacher_id,
            "total_sessions": 0,
            "base_earned": 0.0,
            "bonus_earned": 0.0,
            "total_earned": 0.0,
            "avg_rating": None,
            "avg_credibility": None,
        }

    session_ids = list(session_amounts.keys())
    reviews = (
        sb.client.table("reviews")
        .select("session_id,rating,credibility_score,bonus_percentage")
        .in_("session_id", session_ids)
        .execute()
        .data
        or []
    )

    base_earned = sum(session_amounts.values())
    bonus_earned = 0.0
    ratings = []
    cred_scores = []

    for r in reviews:
        sid = r["session_id"]
        amount = session_amounts.get(sid, 0.0)
        bonus_pct = float(r.get("bonus_percentage") or 0.0)
        bonus_earned += amount * (bonus_pct / 100.0)
        ratings.append(float(r.get("rating") or 0.0))
        cred_scores.append(float(r.get("credibility_score") or 0.0))

    total_sessions = len(sessions)
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    avg_cred = sum(cred_scores) / len(cred_scores) if cred_scores else None

    return {
        "teacher_id": teacher_id,
        "total_sessions": total_sessions,
        "base_earned": round(base_earned, 2),
        "bonus_earned": round(bonus_earned, 2),
        "total_earned": round(base_earned + bonus_earned, 2),
        "avg_rating": round(avg_rating, 2) if avg_rating is not None else None,
        "avg_credibility": round(avg_cred, 3) if avg_cred is not None else None,
    }


@router.get("/quality/{teacher_id}")
def quality_breakdown(teacher_id: str) -> dict:
    """
    List reviews and quality metrics per session for teacher dashboard.
    """
    sb = get_supabase()
    teacher = sb.maybe_single("users", "*", id=teacher_id)
    if not teacher or teacher.get("role") != "teacher":
        raise http_error(404, "Teacher not found", code="TEACHER_NOT_FOUND")

    sessions = (
        sb.client.table("sessions")
        .select("id,listing_id,final_amount_charged,completion_percentage,engagement_metrics")
        .eq("teacher_id", teacher_id)
        .eq("status", "ended")
        .execute()
        .data
        or []
    )
    session_by_id = {s["id"]: s for s in sessions}
    session_ids = list(session_by_id.keys())
    if not session_ids:
        return {"teacher_id": teacher_id, "sessions": [], "reviews": []}

    reviews = (
        sb.client.table("reviews")
        .select("session_id,rating,review_text,credibility_score,bonus_percentage,created_at")
        .in_("session_id", session_ids)
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )

    # group reviews by session
    by_session: dict[str, list[dict]] = defaultdict(list)
    for r in reviews:
        by_session[r["session_id"]].append(r)

    session_quality = []
    for sid, sdata in session_by_id.items():
        s_reviews = by_session.get(sid, [])
        session_quality.append(
            {
                "session_id": sid,
                "listing_id": sdata["listing_id"],
                "final_amount_charged": sdata.get("final_amount_charged"),
                "completion_percentage": sdata.get("completion_percentage"),
                "engagement_metrics": sdata.get("engagement_metrics"),
                "reviews": s_reviews,
            }
        )

    return {"teacher_id": teacher_id, "sessions": session_quality}
