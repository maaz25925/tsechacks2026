#!/usr/bin/env python3
"""
End-to-end test with real data:

1. Login as teacher (or use BEARER_TOKEN)
2. POST /creator/upload with test.mp4, no transcription (AI generates it)
3. GET /discovery/listings/{listing_id} and validate

Requirements:
- Backend running: uv run uvicorn app.main:app --port 8000
- test.mp4 in backend/ or current dir
- Teacher credentials in Supabase Auth (or register first)

Usage:
  cd backend
  set BASE_URL=http://localhost:8000
  set TEACHER_EMAIL=teacher1@murph.dev
  set TEACHER_PASSWORD=your_password
  uv run python test_e2e_upload_and_course_detail.py

  Or with existing token:
  set BEARER_TOKEN=your_jwt_token
  uv run python test_e2e_upload_and_course_detail.py

  Custom video path:
  set VIDEO_PATH=C:\\path\\to\\test.mp4
  uv run python test_e2e_upload_and_course_detail.py
"""

import os
import sys
from pathlib import Path

# Minimal 1x1 PNG (required for thumbnail)
MINIMAL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)

BASE_URL_DEFAULT = "http://localhost:8000"


def find_video_path() -> Path | None:
    video_path = os.environ.get("VIDEO_PATH")
    if video_path and Path(video_path).is_file():
        return Path(video_path)
    for name in ("test.mp4", "backend/test.mp4", "test.mp4"):
        p = Path(name)
        if p.is_file():
            return p
    # cwd when run from backend/
    if Path("test.mp4").is_file():
        return Path("test.mp4")
    return None


def get_base_url() -> str:
    return os.environ.get("BASE_URL", BASE_URL_DEFAULT).rstrip("/")


def get_token(httpx_client) -> str:
    token = os.environ.get("BEARER_TOKEN", "").strip()
    if token:
        return token
    email = os.environ.get("TEACHER_EMAIL", "").strip()
    password = os.environ.get("TEACHER_PASSWORD", "").strip()
    if not email or not password:
        print("ERROR: Set BEARER_TOKEN or (TEACHER_EMAIL + TEACHER_PASSWORD)")
        print("  Example: TEACHER_EMAIL=teacher1@murph.dev TEACHER_PASSWORD=yourpass")
        sys.exit(1)
    url = f"{get_base_url()}/auth/login"
    resp = httpx_client.post(url, json={"email": email, "password": password})
    if resp.status_code != 200:
        print(f"ERROR: Login failed: {resp.status_code} {resp.text}")
        print("  Tip: Register a teacher first: POST /auth/register with role=teacher")
        sys.exit(1)
    data = resp.json()
    access_token = data.get("access_token")
    role = data.get("role", "")
    if not access_token:
        print("ERROR: No access_token in login response (user may need to confirm email)")
        sys.exit(1)
    if role != "teacher":
        print(f"WARNING: Logged-in user role is {role!r}, not teacher. Upload may return 403.")
    return access_token


def upload_course(httpx_client, token: str, video_path: Path) -> str:
    url = f"{get_base_url()}/creator/upload"
    headers = {"Authorization": f"Bearer {token}"}

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    # Multipart: form fields + files
    data = {
        "title": "E2E Test Course (test.mp4)",
        "description": "End-to-end test course with real video. No transcription provided.",
        "category": "testing",
        "visibility": "public",
        "basePrice": 9.99,
    }
    files = [
        ("video", (video_path.name, video_bytes, "video/mp4")),
        ("thumbnail", ("thumb.png", MINIMAL_PNG_BYTES, "image/png")),
    ]

    resp = httpx_client.post(url, data=data, files=files, headers=headers, timeout=60.0)
    if resp.status_code != 200:
        print(f"ERROR: Upload failed: {resp.status_code}")
        try:
            err = resp.json()
            print(err)
        except Exception:
            print(resp.text)
        sys.exit(1)

    result = resp.json()
    listing_id = result.get("listing_id")
    if not listing_id:
        print("ERROR: No listing_id in upload response")
        sys.exit(1)
    return listing_id


def get_course_detail(httpx_client, listing_id: str) -> dict:
    url = f"{get_base_url()}/discovery/listings/{listing_id}"
    resp = httpx_client.get(url, timeout=15.0)
    if resp.status_code != 200:
        print(f"ERROR: Course detail failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    return resp.json()


def main() -> None:
    import httpx

    base_url = get_base_url()
    print("=" * 60)
    print("E2E Test: creator/upload + discovery/listings/{listing_id}")
    print("=" * 60)
    print(f"BASE_URL: {base_url}\n")

    video_path = find_video_path()
    if not video_path:
        print("ERROR: test.mp4 not found.")
        print("  Put test.mp4 in backend/ or set VIDEO_PATH=...")
        sys.exit(1)
    print(f"Video: {video_path} ({video_path.stat().st_size} bytes)\n")

    with httpx.Client(timeout=30.0) as client:
        # 1) Token
        print("Step 1: Get teacher token (login or BEARER_TOKEN)...")
        token = get_token(client)
        print("  Token obtained.\n")

        # 2) Upload
        print("Step 2: POST /creator/upload (video + thumbnail, no transcription)...")
        listing_id = upload_course(client, token, video_path)
        print(f"  listing_id: {listing_id}\n")

        # 3) Course detail
        print(f"Step 3: GET /discovery/listings/{listing_id}...")
        detail = get_course_detail(client, listing_id)
        print("  Response:")
        print("  " + "-" * 50)
        for key, value in detail.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], str) and len(value[0]) > 50:
                print(f"    {key}: [ {value[0][:50]!r}... ] ({len(value)} item(s))")
            elif isinstance(value, list) and len(value) > 2:
                print(f"    {key}: [ ... ] ({len(value)} items)")
            elif isinstance(value, str) and len(value) > 55:
                print(f"    {key}: {value[:55]!r}...")
            else:
                print(f"    {key}: {value!r}")
        print("  " + "-" * 50)

    # Validate
    required = ("title", "description", "category", "video_url", "thumbnail", "reviews_rating", "course_outcomes", "transcription")
    missing = [k for k in required if k not in detail]
    if missing:
        print(f"\nFAIL: Missing fields: {missing}")
        sys.exit(1)
    if not isinstance(detail["video_url"], (str, list)):
        print("\nFAIL: video_url must be string or list")
        sys.exit(1)
    video_url = detail["video_url"]
    if isinstance(video_url, list) and len(video_url) == 0 and detail.get("title"):
        print("\nWARNING: video_url is empty list (listing may not have stored URLs yet).")
    print("\nAll steps OK. E2E test PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
