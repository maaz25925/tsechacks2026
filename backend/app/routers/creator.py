from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile

from app.errors import http_error
from app.schemas import CreatorUploadResponse
from app.supabase_client import get_supabase, utc_now_iso

router = APIRouter(prefix="/creator", tags=["creator"])


@router.post("/upload", response_model=CreatorUploadResponse)
async def upload(
    teacher_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    listing_type: str = Form("single_video"),
    total_duration_min: float = Form(10.0),
    reserve_amount: float = Form(30.0),
    price_per_min: float = Form(1.5),
    tags_json: str = Form("{}"),
    status: str = Form("published"),
    listing_id: str | None = Form(None),
    file: UploadFile = File(...),
) -> CreatorUploadResponse:
    """
    Creator Studio upload.

    Frontend should submit multipart/form-data:
    - file: video file
    - teacher_id, title, etc.

    This endpoint:
    - uploads to Supabase Storage bucket `videos`
    - inserts or updates a listing with the stored URL
    """
    sb = get_supabase()

    teacher = sb.maybe_single("users", "*", id=teacher_id)
    if not teacher or teacher.get("role") != "teacher":
        raise http_error(404, "Teacher not found", code="TEACHER_NOT_FOUND")

    content = await file.read()
    if not content:
        raise http_error(400, "Empty file", code="EMPTY_FILE")

    content_type = file.content_type or "application/octet-stream"
    storage_path = f"{teacher_id}/{uuid4().hex}_{file.filename}"
    uploaded = sb.upload_video(path=storage_path, file_bytes=content, content_type=content_type)
    public_url = uploaded["public_url"]

    # Create or update listing
    lid = listing_id or f"listing_{uuid4().hex}"
    try:
        import json

        tags = json.loads(tags_json) if tags_json else {}
    except Exception:
        tags = {}

    listing = sb.maybe_single("listings", "*", id=lid)
    if listing:
        # append to video_urls
        video_urls = listing.get("video_urls") or []
        if not isinstance(video_urls, list):
            video_urls = []
        video_urls.append(public_url)
        sb.update(
            "listings",
            {
                "title": title or listing.get("title"),
                "description": description or listing.get("description"),
                "type": listing_type or listing.get("type"),
                "total_duration_min": total_duration_min or listing.get("total_duration_min"),
                "reserve_amount": reserve_amount or listing.get("reserve_amount"),
                "price_per_min": price_per_min or listing.get("price_per_min"),
                "tags": tags or listing.get("tags"),
                "status": status or listing.get("status"),
                "video_urls": video_urls,
            },
            match={"id": lid},
        )
    else:
        sb.insert(
            "listings",
            {
                "id": lid,
                "teacher_id": teacher_id,
                "title": title,
                "description": description,
                "type": listing_type,
                "total_duration_min": total_duration_min,
                "reserve_amount": reserve_amount,
                "price_per_min": price_per_min,
                "tags": tags,
                "thumbnail_url": None,
                "status": status,
                "video_urls": [public_url],
                "created_at": utc_now_iso(),
            },
        )

    return CreatorUploadResponse(listing_id=lid, uploaded_url=public_url, storage_path=storage_path)

