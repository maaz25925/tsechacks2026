from __future__ import annotations

from fastapi import APIRouter, Query

from app.errors import http_error
from app.schemas import DiscoverySuggestRequest, DiscoverySuggestResponse, ListingPublic
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

