from __future__ import annotations

from app.config import get_settings
from app.supabase_client import get_supabase, utc_now_iso


def seed_fake_data() -> None:
    """
    Seed 2 teachers, 1 student, 5 listings.

    This is intentionally idempotent using fixed IDs + upserts.
    """
    s = get_settings()
    if not s.supabase_url or not s.supabase_key:
        # Allow running the API without Supabase during local iteration.
        return

    sb = get_supabase()

    teachers = [
        {
            "id": "teacher_1",
            "email": "teacher1@murph.dev",
            "role": "teacher",
            "name": "Aisha Patel",
            "bio": "Certified yoga & meditation coach.",
            "wallet_address": None,
            "created_at": utc_now_iso(),
        },
        {
            "id": "teacher_2",
            "email": "teacher2@murph.dev",
            "role": "teacher",
            "name": "Marco Silva",
            "bio": "Guitar teacher (fingerstyle + rhythm).",
            "wallet_address": None,
            "created_at": utc_now_iso(),
        },
    ]
    student = {
        "id": "student_1",
        "email": "student@murph.dev",
        "role": "student",
        "name": "Jamie Chen",
        "bio": "Trying new skills on a budget.",
        "wallet_address": None,
        "created_at": utc_now_iso(),
    }

    for t in teachers:
        sb.upsert("users", t, on_conflict="id")
    sb.upsert("users", student, on_conflict="id")

    listings = [
        {
            "id": "listing_1",
            "teacher_id": "teacher_1",
            "title": "10-min Morning Meditation Reset",
            "description": "Guided breathing + mindful check-in for busy days.",
            "type": "single_video",
            "total_duration_min": 10,
            "reserve_amount": 30.0,
            "price_per_min": 1.5,
            "tags": {"category": "meditation", "level": "beginner"},
            "thumbnail_url": None,
            "status": "published",
            "video_urls": [],
            "created_at": utc_now_iso(),
        },
        {
            "id": "listing_2",
            "teacher_id": "teacher_1",
            "title": "Yoga Flow: Lower Back Relief",
            "description": "Gentle sequence to reduce stiffness and improve mobility.",
            "type": "single_video",
            "total_duration_min": 18,
            "reserve_amount": 30.0,
            "price_per_min": 1.8,
            "tags": {"category": "fitness", "focus": "mobility"},
            "thumbnail_url": None,
            "status": "published",
            "video_urls": [],
            "created_at": utc_now_iso(),
        },
        {
            "id": "listing_3",
            "teacher_id": "teacher_2",
            "title": "Guitar: 3 Chords You Can Use Everywhere",
            "description": "A quick-start lesson for rhythm guitar (with practice track).",
            "type": "single_video",
            "total_duration_min": 15,
            "reserve_amount": 30.0,
            "price_per_min": 2.0,
            "tags": {"category": "music", "instrument": "guitar"},
            "thumbnail_url": None,
            "status": "published",
            "video_urls": [],
            "created_at": utc_now_iso(),
        },
        {
            "id": "listing_4",
            "teacher_id": "teacher_2",
            "title": "Fingerstyle Foundations (Mini Course)",
            "description": "3 short videos to get your right-hand technique solid.",
            "type": "multi_video_course",
            "total_duration_min": 30,
            "reserve_amount": 30.0,
            "price_per_min": 1.6,
            "tags": {"category": "music", "course": True},
            "thumbnail_url": None,
            "status": "published",
            "video_urls": [],
            "created_at": utc_now_iso(),
        },
        {
            "id": "listing_5",
            "teacher_id": "teacher_1",
            "title": "Breathwork for Stress (Multi)",
            "description": "A 4-part breathwork series. Pay per use, no permanent access.",
            "type": "multi_video_course",
            "total_duration_min": 40,
            "reserve_amount": 30.0,
            "price_per_min": 1.2,
            "tags": {"category": "meditation", "series": True},
            "thumbnail_url": None,
            "status": "published",
            "video_urls": [],
            "created_at": utc_now_iso(),
        },
    ]

    for l in listings:
        sb.upsert("listings", l, on_conflict="id")

