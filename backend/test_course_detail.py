#!/usr/bin/env python3
"""
Test GET /discovery/listings/{listing_id} (Get Course Detail).

Usage:
  # Run against in-process app (no server needed; needs Supabase configured):
  uv run python test_course_detail.py

  # Run against a running server (start server first: uv run uvicorn app.main:app --port 8000):
  BASE_URL=http://localhost:8000 uv run python test_course_detail.py

  # With a specific listing_id:
  LISTING_ID=listing_1 uv run python test_course_detail.py
"""

import os
import sys
from pathlib import Path

# Ensure backend app is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Required fields in CourseDetailResponse
COURSE_DETAIL_FIELDS = [
    "title",
    "description",
    "category",
    "teacher_name",
    "video_url",
    "thumbnail",
    "reviews_rating",
    "course_outcomes",
    "transcription",
]


def test_via_http(base_url: str, listing_id: str) -> dict:
    """Call GET /discovery/listings/{listing_id} via HTTP."""
    import httpx

    url = f"{base_url.rstrip('/')}/discovery/listings/{listing_id}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url)
    resp.raise_for_status()
    return resp.json()


def test_via_test_client(listing_id: str) -> dict:
    """Call GET /discovery/listings/{listing_id} via FastAPI TestClient (no server)."""
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    resp = client.get(f"/discovery/listings/{listing_id}")
    resp.raise_for_status()
    return resp.json()


def get_first_listing_id(base_url: str | None) -> str | None:
    """Fetch first listing ID from GET /discovery/listings (for real server)."""
    import httpx

    url = f"{base_url.rstrip('/')}/discovery/listings?limit=1"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if not data or not isinstance(data, list):
        return None
    first = data[0]
    return first.get("id") if isinstance(first, dict) else None


def get_first_listing_id_test_client() -> str | None:
    """Fetch first listing ID via TestClient."""
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    resp = client.get("/discovery/listings?limit=1")
    if resp.status_code != 200:
        return None
    data = resp.json()
    if not data or not isinstance(data, list):
        return None
    first = data[0]
    return first.get("id") if isinstance(first, dict) else None


def validate_course_detail_response(data: dict) -> list[str]:
    """Validate response shape. Returns list of error messages (empty if valid)."""
    errors = []
    for field in COURSE_DETAIL_FIELDS:
        if field not in data:
            errors.append(f"Missing field: {field}")
    if "video_url" in data:
        v = data["video_url"]
        if not isinstance(v, (str, list)):
            errors.append("video_url must be string or list of strings")
        elif isinstance(v, list) and not all(isinstance(x, str) for x in v):
            errors.append("video_url list must contain only strings")
    if "reviews_rating" in data and data["reviews_rating"] is not None:
        if not isinstance(data["reviews_rating"], (int, float)):
            errors.append("reviews_rating must be number or null")
    if "course_outcomes" in data and data["course_outcomes"] is not None:
        if not isinstance(data["course_outcomes"], list):
            errors.append("course_outcomes must be list or null")
    if "title" in data and not isinstance(data["title"], str):
        errors.append("title must be string")
    if "description" in data and not isinstance(data["description"], str):
        errors.append("description must be string")
    if "category" in data and not isinstance(data["category"], str):
        errors.append("category must be string")
    if "thumbnail" in data and not isinstance(data["thumbnail"], str):
        errors.append("thumbnail must be string")
    return errors


def run_tests() -> bool:
    base_url = os.environ.get("BASE_URL")
    listing_id = os.environ.get("LISTING_ID")

    if base_url:
        # Hit real server
        print(f"Using BASE_URL: {base_url}")
        if not listing_id:
            print("Fetching first listing_id from GET /discovery/listings...")
            listing_id = get_first_listing_id(base_url)
        if not listing_id:
            listing_id = "listing_1"
            print(f"No listing found; using default: {listing_id}")
        try:
            data = test_via_http(base_url, listing_id)
        except Exception as e:
            print(f"FAIL: Request failed: {e}")
            return False
    else:
        # Use TestClient (in-process)
        print("Using FastAPI TestClient (in-process, no server).")
        if not listing_id:
            print("Fetching first listing_id from GET /discovery/listings...")
            listing_id = get_first_listing_id_test_client()
        if not listing_id:
            listing_id = "listing_1"
            print(f"No listing from catalog; using default: {listing_id}")
        try:
            data = test_via_test_client(listing_id)
        except Exception as e:
            print(f"FAIL: Request failed: {e}")
            return False

    print(f"\nGET /discovery/listings/{listing_id}")
    print("Response (200 OK):")
    print("-" * 50)
    for key in COURSE_DETAIL_FIELDS:
        val = data.get(key)
        if isinstance(val, list) and len(val) > 3:
            print(f"  {key}: [{val[0]!r}, ... ({len(val)} items)]")
        elif isinstance(val, str) and len(val) > 60:
            print(f"  {key}: {val[:60]!r}...")
        else:
            print(f"  {key}: {val!r}")
    print("-" * 50)

    errors = validate_course_detail_response(data)
    if errors:
        print("Validation FAIL:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("Validation PASS: All required fields present and correctly typed.")
    return True


def test_404() -> bool:
    """Test that non-existent listing_id returns 404."""
    base_url = os.environ.get("BASE_URL")
    fake_id = "nonexistent_listing_999"

    if base_url:
        import httpx

        url = f"{base_url.rstrip('/')}/discovery/listings/{fake_id}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
        if resp.status_code != 404:
            print(f"FAIL: Expected 404 for {fake_id}, got {resp.status_code}")
            return False
        return True
    else:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        resp = client.get(f"/discovery/listings/{fake_id}")
        if resp.status_code != 404:
            print(f"FAIL: Expected 404 for {fake_id}, got {resp.status_code}")
            return False
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("Test: GET /discovery/listings/{listing_id} (Get Course Detail)")
    print("=" * 60)

    ok = run_tests()
    print()
    print("Test 404 (non-existent listing_id):")
    ok_404 = test_404()
    if ok_404:
        print("  404 test PASS")
    else:
        print("  404 test FAIL")

    if ok and ok_404:
        print("\nAll tests PASSED.")
        sys.exit(0)
    sys.exit(1)
