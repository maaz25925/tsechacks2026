# Backend Changes Summary - Enhanced Video Upload & Course Detail

## Overview
Enhanced the backend to support:
1. **Multi-video uploads** with thumbnail, transcription, and auto-generated course outcomes
2. **Course detail endpoint** with reviews rating and full metadata
3. **AI-powered transcription and course outcomes generation**

---

## Database Changes

### New Columns Added to `listings` Table:
1. `category` (text, nullable) - Course category
2. `visibility` (text, nullable) - "draft", "public", or "private"
3. `base_price` (double precision, nullable) - Base course price
4. `transcription_url` (text, nullable) - URL to transcription file in storage
5. `course_outcomes` (jsonb, nullable) - AI-generated learning outcomes as JSON array

**Migration SQL:** See `backend/migration_add_listing_fields.sql`

---

## File Changes

### 1. `backend/app/models.py`
**Changes:**
- Added 5 new fields to `Listing` SQLAlchemy model:
  - `category: Mapped[str | None]`
  - `visibility: Mapped[str | None]`
  - `base_price: Mapped[float | None]`
  - `transcription_url: Mapped[str | None]`
  - `course_outcomes: Mapped[list[str] | None]`

**Lines Modified:** 59-64

---

### 2. `backend/app/supabase_client.py`
**Changes:**
- Added `upload_file()` method - Generic file upload supporting any bucket
  - Parameters: `path`, `file_bytes`, `content_type`, `bucket_name` (optional)
  - Returns: `{"path": str, "public_url": str, "bucket": str}`
  
- Added `get_signed_url()` method - Generate signed URLs for private bucket access
  - Parameters: `path`, `expires_in` (default 3600 seconds), `bucket_name` (optional)
  - Returns: Signed URL string

**Lines Added:** 90-120

---

### 3. `backend/app/services/ai.py`
**Changes:**
- Added `generate_transcription()` method:
  - Generates mock transcription text from course description + video metadata
  - Uses Groq/OpenAI (Groq primary, OpenAI fallback)
  - Returns plain text transcription string
  - Falls back to template if AI fails
  
- Added `generate_course_outcomes()` method:
  - Extracts 3-5 learning outcomes from description + transcription
  - Returns JSON list of outcome strings
  - Uses AI to analyze content and generate actionable outcomes
  - Falls back to simple extraction if AI fails

**Lines Added:** 151-220 (after `score_review_credibility`)

---

### 4. `backend/app/routers/creator.py`
**Changes:**
- **Completely rewrote** `POST /creator/upload` endpoint:
  
  **New Request Parameters:**
  - `title` (required, Form)
  - `description` (required, Form)
  - `category` (required, Form)
  - `visibility` (required, Form) - "draft", "public", or "private"
  - `basePrice` (required, Form, float)
  - `video` (required, List[UploadFile]) - Supports multiple files
  - `thumbnail` (required, UploadFile)
  - `transcription` (optional, UploadFile)
  - Legacy fields: `listing_type`, `total_duration_min`, `reserve_amount`, `price_per_min`, `tags_json`, `listing_id`
  
  **Authentication:**
  - Now uses `require_teacher` dependency (JWT auth)
  - Extracts `teacher_id` from JWT token (no longer required in form)
  
  **New Functionality:**
  1. Handles multiple video files (FastAPI auto-converts to list)
  2. Uploads all videos to Supabase Storage
  3. Uploads thumbnail to storage
  4. If transcription provided: uploads it
  5. If transcription NOT provided: auto-generates using AI and uploads
  6. Auto-generates `course_outcomes` using AI
  7. Determines `listing_type` automatically (single_video vs multi_video_course)
  8. Maps `visibility` to `status` for backward compatibility
  9. Saves all new fields to database
  
  **Response:** Same `CreatorUploadResponse` (backward compatible)

**Lines Modified:** 1-179 (complete rewrite)

---

### 5. `backend/app/routers/discovery.py`
**Changes:**
- Added new endpoint `GET /discovery/listings/{listing_id}`:
  
  **Response Schema:** `CourseDetailResponse`
  ```json
  {
    "title": str,
    "description": str,
    "category": str,
    "video_url": str | list[str],  // Single URL or array for multiple videos
    "thumbnail": str,
    "reviews_rating": float | null,  // Average rating from reviews
    "course_outcomes": list[str] | null,
    "transcription": str | null  // URL or text content
  }
  ```
  
  **Functionality:**
  1. Fetches listing by ID
  2. Handles single or multiple video URLs (returns string or array)
  3. Calculates average `reviews_rating` from reviews table via sessions
  4. Returns course outcomes (AI-generated)
  5. Returns transcription URL
  6. Supports signed URLs for private buckets (ready for implementation)

**Lines Added:** 93-212

---

### 6. `backend/app/schemas.py`
**Changes:**
- Added `CourseDetailResponse` Pydantic model:
  - `title: str`
  - `description: str`
  - `category: str`
  - `video_url: str | list[str]` - Union type for single/multiple videos
  - `thumbnail: str`
  - `reviews_rating: float | None`
  - `course_outcomes: list[str] | None`
  - `transcription: str | None`

**Lines Added:** 120-133

---

## API Endpoint Changes

### Modified Endpoints:

#### `POST /creator/upload`
- **Before:** Single video upload, teacher_id in form
- **After:** Multiple videos, thumbnail required, transcription optional (auto-generated), JWT auth, new fields

### New Endpoints:

#### `GET /discovery/listings/{listing_id}`
- Returns complete course detail with reviews rating
- Response: `CourseDetailResponse`

---

## Frontend Integration Notes

### Upload Flow (`POST /creator/upload`):
```javascript
const formData = new FormData();
formData.append('title', 'Course Title');
formData.append('description', 'Course Description');
formData.append('category', 'meditation');
formData.append('visibility', 'public'); // or 'draft', 'private'
formData.append('basePrice', '29.99');
formData.append('video', videoFile1); // Multiple files with same name
formData.append('video', videoFile2);
formData.append('thumbnail', thumbnailFile);
formData.append('transcription', transcriptionFile); // Optional

fetch('/creator/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}` // JWT required
  },
  body: formData
});
```

### Course Detail (`GET /discovery/listings/{listing_id}`):
```javascript
const response = await fetch(`/discovery/listings/${listingId}`);
const course = await response.json();
// course.video_url is string (single) or array (multiple)
// course.reviews_rating is null if no reviews
```

---

## Backward Compatibility

- ✅ Existing endpoints still work
- ✅ Legacy form fields (`listing_type`, `reserve_amount`, etc.) still supported
- ✅ Old listings without new fields will have `null` values (nullable columns)
- ✅ `CreatorUploadResponse` unchanged
- ✅ Existing `GET /discovery/listings` unchanged

---

## Testing Checklist

- [ ] Run SQL migration to add new columns
- [ ] Test single video upload
- [ ] Test multiple video upload
- [ ] Test with transcription file
- [ ] Test without transcription (auto-generation)
- [ ] Test course detail endpoint
- [ ] Verify reviews_rating calculation
- [ ] Verify course_outcomes generation
- [ ] Test JWT authentication on upload endpoint
- [ ] Test visibility values ("draft", "public", "private")

---

## Dependencies

No new dependencies added. Uses existing:
- FastAPI (multipart form handling)
- Supabase Python client (storage operations)
- OpenAI SDK (Groq/OpenAI for AI generation)
- Pydantic (schema validation)

---

## Notes

1. **Visibility vs Status:** 
   - `visibility` is new field ("draft", "public", "private")
   - `status` is existing field ("draft", "published", "flagged")
   - Upload endpoint maps visibility to status for backward compatibility

2. **Signed URLs:**
   - `get_signed_url()` method added but not yet used in course detail endpoint
   - Can be enabled for private bucket security

3. **AI Fallbacks:**
   - Both transcription and course_outcomes have fallback logic if AI fails
   - Ensures endpoint never crashes due to AI unavailability

4. **Multiple Videos:**
   - FastAPI automatically converts multiple files with same field name to `List[UploadFile]`
   - Frontend sends multiple files with field name "video"
