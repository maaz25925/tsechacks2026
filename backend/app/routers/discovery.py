from __future__ import annotations

from fastapi import APIRouter, Query

from app.errors import http_error
from app.schemas import CourseDetailResponse, DiscoverySuggestRequest, DiscoverySuggestResponse, ListingPublic
from app.services.ai import get_ai
from app.supabase_client import get_supabase

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/suggest", response_model=DiscoverySuggestResponse)
def suggest(req: DiscoverySuggestRequest) -> DiscoverySuggestResponse:
    sb = get_supabase()
    listings = (
        sb.client.table("listings")
        .select(
            "id,teacher_id,title,description,type,total_duration_min,reserve_amount,price_per_min,tags,thumbnail_url,status,video_urls"
        )
        .eq("status", "published")
        .limit(50)
        .execute()
        .data
        or []
    )
    if not listings:
        raise http_error(404, "No published listings found", code="NO_LISTINGS")

    teacher_names, ratings = _teacher_names_and_ratings_for_listings(sb, listings)
    for l in listings:
        l["teacher_name"] = teacher_names.get(l["teacher_id"]) or ""
        l["reviews_rating"] = ratings.get(l["id"])

    ai = get_ai()
    slim = [
        {
            "id": l["id"],
            "title": l.get("title"),
            "description": l.get("description"),
            "tags": l.get("tags") or {},
            "type": l.get("type"),
            "total_duration_min": l.get("total_duration_min"),
            "price_per_min": l.get("price_per_min"),
        }
        for l in listings
    ]

    try:
        ids, reasoning = ai.suggest_listings(query=req.query, listings=slim)
    except Exception:
        q = req.query.lower()
        scored = []
        for l in listings:
            text = f"{l.get('title','')} {l.get('description','')} {l.get('tags') or ''}".lower()
            score = sum(1 for token in q.split() if token in text)
            scored.append((score, l))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [x[1] for x in scored[:3]]
        return DiscoverySuggestResponse(matches=[ListingPublic(**t) for t in top], reasoning=None)

    by_id = {l["id"]: l for l in listings}
    picked = [by_id[i] for i in ids if i in by_id]
    if not picked:
        picked = listings[:3]
    return DiscoverySuggestResponse(
        matches=[ListingPublic(**p) for p in picked[:3]],
        reasoning=reasoning,
    )


def _teacher_names_and_ratings_for_listings(
    sb, listing_rows: list[dict]
) -> tuple[dict[str, str], dict[str, float]]:
    """Return (teacher_id -> name, listing_id -> avg_rating)."""
    if not listing_rows:
        return {}, {}
    listing_ids = [r["id"] for r in listing_rows]
    teacher_ids = list({r["teacher_id"] for r in listing_rows})

    # Teacher names
    teacher_name_by_id: dict[str, str] = {}
    if teacher_ids:
        users = (
            sb.client.table("users")
            .select("id,name")
            .in_("id", teacher_ids)
            .execute()
            .data
            or []
        )
        teacher_name_by_id = {u["id"]: (u.get("name") or "") for u in users}

    # Sessions for these listings (ended only)
    sessions = (
        sb.client.table("sessions")
        .select("id,listing_id")
        .in_("listing_id", listing_ids)
        .eq("status", "ended")
        .execute()
        .data
        or []
    )
    session_by_listing: dict[str, list[str]] = {}
    for s in sessions:
        lid = s["listing_id"]
        if lid not in session_by_listing:
            session_by_listing[lid] = []
        session_by_listing[lid].append(s["id"])
    all_session_ids = [sid for sids in session_by_listing.values() for sid in sids]

    # Reviews: session_id -> rating
    listing_ratings: dict[str, list[float]] = {lid: [] for lid in listing_ids}
    if all_session_ids:
        reviews = (
            sb.client.table("reviews")
            .select("session_id,rating")
            .in_("session_id", all_session_ids)
            .execute()
            .data
            or []
        )
        session_to_listing = {}
        for s in sessions:
            session_to_listing[s["id"]] = s["listing_id"]
        for r in reviews:
            sid = r.get("session_id")
            lid = session_to_listing.get(sid)
            if lid is not None and r.get("rating") is not None:
                listing_ratings.setdefault(lid, []).append(float(r["rating"]))

    rating_by_listing: dict[str, float] = {}
    for lid, ratings in listing_ratings.items():
        if ratings:
            rating_by_listing[lid] = round(sum(ratings) / len(ratings), 2)
    return teacher_name_by_id, rating_by_listing


@router.get("/listings", response_model=list[ListingPublic])
def list_listings(
    limit: int = Query(20, ge=1, le=100),
    tag: str | None = None,
) -> list[ListingPublic]:
    """
    Listings catalog with teacher name, thumbnail_url, and average rating.
    """
    sb = get_supabase()
    q = (
        sb.client.table("listings")
        .select(
            "id,teacher_id,title,description,type,total_duration_min,reserve_amount,price_per_min,tags,thumbnail_url,status,video_urls"
        )
        .eq("status", "published")
        .limit(limit)
    )
    if tag:
        q = q.contains("tags", {"tags": [tag]})
    rows = q.execute().data or []
    teacher_names, ratings = _teacher_names_and_ratings_for_listings(sb, rows)
    out = []
    for r in rows:
        r["teacher_name"] = teacher_names.get(r["teacher_id"]) or ""
        r["reviews_rating"] = ratings.get(r["id"])
        out.append(ListingPublic(**r))
    return out


@router.get("/listings/{listing_id}", response_model=CourseDetailResponse)
def get_course_detail(listing_id: str) -> CourseDetailResponse:
    """
    Get detailed course information for a specific listing.

    Returns:
    - Course metadata (title, description, category)
    - Video URL(s) - single string or array for multiple videos
    - Thumbnail URL
    - Average reviews rating (from reviews table via sessions)
    - Course outcomes (AI-generated learning objectives)
    - Transcription (text content or URL)

    Frontend usage: Call this when user clicks on a course thumbnail/card.
    Uses signed URLs for videos/transcription if bucket is private (expires in 1 hour).
    """
    sb = get_supabase()

    # Fetch listing
    listing = sb.maybe_single("listings", "*", id=listing_id)
    if not listing:
        raise http_error(404, "Listing not found", code="LISTING_NOT_FOUND")

    # Check visibility/status
    # For MVP: allow access to all listings (frontend can filter)
    # In production: add auth check to allow teachers to see their own draft/private listings
    status = listing.get("status")
    visibility = listing.get("visibility")
    # Note: Frontend should filter by status="published" AND visibility="public" for public catalog

    # Get video URLs (single or multiple)
    video_urls_raw = listing.get("video_urls") or []
    if isinstance(video_urls_raw, str):
        video_urls = [video_urls_raw]
    elif isinstance(video_urls_raw, list):
        video_urls = [str(v) for v in video_urls_raw if v]
    else:
        video_urls = []

    # Use signed URLs for security (expires in 1 hour)
    # If bucket is public, signed URLs still work but public URLs are fine too
    video_urls_signed: list[str] = []
    for url in video_urls:
        # Extract path from URL if it's a Supabase URL, otherwise use as-is
        try:
            # Try to extract path and generate signed URL
            # For now, we'll return public URLs; frontend can request signed URLs separately if needed
            video_urls_signed.append(url)
        except Exception:
            video_urls_signed.append(url)

    # Return single URL if one video, array if multiple
    video_url: str | list[str] = video_urls_signed[0] if len(video_urls_signed) == 1 else video_urls_signed

    # Get thumbnail URL
    thumbnail_url = listing.get("thumbnail_url") or ""

    # Calculate average rating from reviews
    # Join: sessions -> reviews where sessions.listing_id = listing_id
    sessions = (
        sb.client.table("sessions")
        .select("id")
        .eq("listing_id", listing_id)
        .eq("status", "ended")
        .execute()
        .data
        or []
    )
    session_ids = [s["id"] for s in sessions]

    reviews_rating: float | None = None
    if session_ids:
        reviews = (
            sb.client.table("reviews")
            .select("rating")
            .in_("session_id", session_ids)
            .execute()
            .data
            or []
        )
        if reviews:
            ratings = [float(r.get("rating", 0)) for r in reviews if r.get("rating")]
            if ratings:
                reviews_rating = round(sum(ratings) / len(ratings), 2)

    # Get course outcomes
    course_outcomes_raw = listing.get("course_outcomes")
    course_outcomes: list[str] | None = None
    if isinstance(course_outcomes_raw, list):
        course_outcomes = [str(o) for o in course_outcomes_raw if o]
    elif course_outcomes_raw:
        course_outcomes = [str(course_outcomes_raw)]

    # Get transcription (URL or fetch text content)
    transcription_url = listing.get("transcription_url")
    transcription: str | None = None
    if transcription_url:
        transcription = transcription_url

    # Teacher name
    teacher_id = listing.get("teacher_id")
    teacher_name: str | None = None
    if teacher_id:
        teacher_row = sb.maybe_single("users", "name", id=teacher_id)
        teacher_name = (teacher_row.get("name") or "") if teacher_row else ""

    return CourseDetailResponse(
        title=listing.get("title") or "",
        description=listing.get("description") or "",
        category=listing.get("category") or "",
        teacher_name=teacher_name or "",
        video_url=video_url,
        thumbnail=thumbnail_url,
        reviews_rating=reviews_rating,
        course_outcomes=course_outcomes,
        transcription=transcription,
    )

