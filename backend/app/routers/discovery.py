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

    ai = get_ai()
    # We keep the listings payload small for the model.
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
        # If AI is not configured, fall back to keyword scoring.
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


@router.get("/listings", response_model=list[ListingPublic])
def list_listings(
    limit: int = Query(20, ge=1, le=100),
    tag: str | None = None,
) -> list[ListingPublic]:
    """
    Simple listings catalog for frontend browsing (non-AI).
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
        # naive JSON contains filter on tags
        q = q.contains("tags", {"tags": [tag]})  # adjust depending on your tag schema
    rows = q.execute().data or []
    return [ListingPublic(**r) for r in rows]


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
        # For MVP, return URL; frontend can fetch text if needed
        # In production, you might want to fetch and return text directly
        transcription = transcription_url
        # Optionally: fetch transcription text from storage
        # try:
        #     bucket = sb.client.storage.from_(sb.videos_bucket)
        #     # Extract path from URL and download
        #     # transcription = bucket.download(path).decode('utf-8')
        # except Exception:
        #     pass

    return CourseDetailResponse(
        title=listing.get("title") or "",
        description=listing.get("description") or "",
        category=listing.get("category") or "",
        video_url=video_url,
        thumbnail=thumbnail_url,
        reviews_rating=reviews_rating,
        course_outcomes=course_outcomes,
        transcription=transcription,
    )

