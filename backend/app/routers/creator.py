from __future__ import annotations

import json
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.deps import require_teacher
from app.errors import http_error
from app.schemas import CreatorUploadResponse
from app.services.ai import get_ai
from app.supabase_client import get_supabase, utc_now_iso

router = APIRouter(prefix="/creator", tags=["creator"])


@router.post("/upload", response_model=CreatorUploadResponse)
async def upload(
    # Required text fields
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    visibility: str = Form(...),  # "draft", "public", "private"
    basePrice: float = Form(...),
    # File uploads
    # Frontend can send multiple files with field name "video" (FastAPI will auto-convert to list)
    # Or send single file (will be treated as list with one item)
    video: List[UploadFile] = File(...),
    thumbnail: UploadFile = File(...),
    transcription: UploadFile | None = File(None),
    # Optional legacy fields (for backward compatibility)
    listing_type: str = Form("single_video"),
    total_duration_min: float = Form(10.0),
    reserve_amount: float = Form(30.0),
    price_per_min: float = Form(1.5),
    tags_json: str = Form("{}"),
    listing_id: str | None = Form(None),
    # Auth: get teacher from JWT
    teacher: dict = Depends(require_teacher),
) -> CreatorUploadResponse:
    """
    Enhanced Creator Studio upload endpoint.

    Frontend should submit multipart/form-data with:
    - title, description, category, visibility, basePrice (required)
    - video: UploadFile(s) - send multiple files with same field name "video" for multi-video courses
      (FastAPI automatically converts to List[UploadFile])
    - thumbnail: UploadFile (required)
    - transcription: UploadFile (optional; auto-generated if not provided)
    - listing_id: optional (for updating existing listing)

    This endpoint:
    - Uploads video(s), thumbnail, and transcription to Supabase Storage
    - Auto-generates transcription if not provided (using AI from description + metadata)
    - Auto-generates course_outcomes (using AI from description + transcription)
    - Creates/updates a listing with all metadata
    - Returns listing_id and preview URLs

    Note: teacher_id is extracted from JWT token (require_teacher dependency).
    Visibility values: "draft", "public", "private"
    """
    sb = get_supabase()
    ai = get_ai()
    teacher_id = teacher["id"]

    # Validate visibility
    if visibility not in ("draft", "public", "private"):
        raise http_error(400, "visibility must be 'draft', 'public', or 'private'", code="INVALID_VISIBILITY")

    # video is already a list from FastAPI (even if frontend sends single file)
    video_files = video
    if not video_files or len(video_files) == 0:
        raise http_error(400, "At least one video file is required", code="NO_VIDEO")

    # Upload videos
    video_urls: list[str] = []
    teacher_dir = f"{teacher_id}/{uuid4().hex}"
    for idx, vid_file in enumerate(video_files):
        content = await vid_file.read()
        if not content:
            raise http_error(400, f"Empty video file: {vid_file.filename}", code="EMPTY_FILE")
        content_type = vid_file.content_type or "video/mp4"
        storage_path = f"{teacher_dir}/video_{idx}_{vid_file.filename or 'video.mp4'}"
        uploaded = sb.upload_file(path=storage_path, file_bytes=content, content_type=content_type)
        video_urls.append(uploaded["public_url"])

    # Upload thumbnail
    thumb_content = await thumbnail.read()
    if not thumb_content:
        raise http_error(400, "Empty thumbnail file", code="EMPTY_THUMBNAIL")
    thumb_content_type = thumbnail.content_type or "image/jpeg"
    thumb_path = f"{teacher_dir}/thumb_{thumbnail.filename or 'thumbnail.jpg'}"
    thumb_uploaded = sb.upload_file(path=thumb_path, file_bytes=thumb_content, content_type=thumb_content_type)
    thumbnail_url = thumb_uploaded["public_url"]

    # Handle transcription
    transcription_url: str | None = None
    transcription_text: str | None = None

    if transcription:
        # Upload provided transcription file
        trans_content = await transcription.read()
        if trans_content:
            trans_content_type = transcription.content_type or "text/plain"
            trans_path = f"{teacher_dir}/transcription_{transcription.filename or 'transcription.txt'}"
            trans_uploaded = sb.upload_file(path=trans_path, file_bytes=trans_content, content_type=trans_content_type)
            transcription_url = trans_uploaded["public_url"]
            # Read text for course_outcomes generation
            try:
                transcription_text = trans_content.decode("utf-8")
            except Exception:
                transcription_text = None
    else:
        # Generate transcription using AI
        video_metadata = {
            "duration_min": total_duration_min,
            "category": category,
        }
        transcription_text = ai.generate_transcription(description=description, video_metadata=video_metadata)
        # Upload generated transcription as .txt file
        trans_bytes = transcription_text.encode("utf-8")
        trans_path = f"{teacher_dir}/transcription_generated.txt"
        trans_uploaded = sb.upload_file(path=trans_path, file_bytes=trans_bytes, content_type="text/plain")
        transcription_url = trans_uploaded["public_url"]

    # Generate course_outcomes using AI
    course_outcomes = ai.generate_course_outcomes(description=description, transcription=transcription_text)

    # Determine listing type based on number of videos
    if len(video_urls) > 1:
        listing_type = "multi_video_course"
    else:
        listing_type = "single_video"

    # Parse tags if provided
    try:
        tags = json.loads(tags_json) if tags_json else {}
    except Exception:
        tags = {}

    # Map visibility to status (for backward compatibility)
    status_map = {"draft": "draft", "public": "published", "private": "draft"}
    status = status_map.get(visibility, "draft")

    # Create or update listing
    lid = listing_id or f"listing_{uuid4().hex}"
    listing_data = {
        "id": lid,
        "teacher_id": teacher_id,
        "title": title,
        "description": description,
        "category": category,
        "visibility": visibility,
        "base_price": basePrice,
        "type": listing_type,
        "total_duration_min": total_duration_min,
        "reserve_amount": reserve_amount,
        "price_per_min": price_per_min,
        "tags": tags,
        "thumbnail_url": thumbnail_url,
        "status": status,
        "video_urls": video_urls,
        "transcription_url": transcription_url,
        "course_outcomes": course_outcomes,
        "created_at": utc_now_iso(),
    }

    print(f"DEBUG: Attempting to insert/update listing: {lid} with teacher_id {teacher_id}")
    try:
        existing = sb.maybe_single("listings", "*", id=lid)
        if existing:
            # Update existing listing
            print(f"DEBUG: Updating existing listing {lid}")
            sb.update("listings", listing_data, match={"id": lid})
        else:
            # Create new listing
            print(f"DEBUG: Inserting new listing {lid}")
            sb.insert("listings", listing_data)
        print(f"DEBUG: Successfully handled listing {lid}")
    except Exception as e:
        print(f"ERROR: Failed to insert/update listing {lid}: {e}")
        raise http_error(500, f"Database error: {str(e)}", code="DB_ERROR")

    # Return first video URL for backward compatibility (or all URLs joined)
    preview_url = video_urls[0] if video_urls else ""
    return CreatorUploadResponse(listing_id=lid, uploaded_url=preview_url, storage_path=teacher_dir)


@router.get("/listings/{teacher_id}")
def teacher_listings(teacher_id: str) -> dict:
    """
    Return all listings for a given teacher (for Creator dashboard).
    """
    sb = get_supabase()
    rows = (
        sb.client.table("listings")
        .select("*")
        .eq("teacher_id", teacher_id)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
        .data
        or []
    )
    return {"teacher_id": teacher_id, "listings": rows}

