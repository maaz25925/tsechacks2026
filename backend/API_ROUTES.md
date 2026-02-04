# Murph Backend — API Routes

This document lists the backend API routes, methods, brief descriptions, request/response schemas, and auth notes.

Schemas live in: [backend/app/schemas.py](app/schemas.py)
Routers live in: [backend/app/routers](app/routers)

---

## Auth
- POST /auth/register
  - Description: Register a new user (Supabase Auth + profile row).
  - Request: `RegisterRequest` (email, password, role, name, bio)
  - Response: `AuthResponse` (user_id, access_token, role)
  - Auth: none

- POST /auth/login
  - Description: Login using Supabase; returns access token and role.
  - Request: `LoginRequest` (email, password)
  - Response: `AuthResponse` (user_id, access_token, role)
  - Auth: none

---

## Users
- POST /users
  - Description: Create user profile (student or teacher). Password/Auth handled via /auth.
  - Request: `UserCreateRequest`
  - Response: `UserResponse`
  - Auth: none (backend expects auth via Supabase in production)

- GET /users
  - Description: List users (optional `role` filter, pagination `limit` & `offset`).
  - Response: `UserListResponse`

- GET /users/{user_id}
  - Description: Retrieve a user's profile.
  - Response: `UserResponse`

- PUT /users/{user_id}
  - Description: Update a user's profile (name, bio).
  - Request: `UserUpdateRequest`
  - Response: `UserResponse`

- DELETE /users/{user_id}
  - Description: Delete a user.
  - Response: JSON message

---

## Creator (Listing Upload)
- POST /creator/upload
  - Description: Teacher-only multipart upload endpoint for videos, thumbnail, transcription; creates/updates listing.
  - Request: multipart/form-data (title, description, category, visibility, basePrice, video files, thumbnail, transcription optional, etc.)
  - Response: `CreatorUploadResponse` (listing_id, uploaded_url, storage_path)
  - Auth: teacher (uses `require_teacher` dependency)

- GET /creator/listings/{teacher_id}
  - Description: Get listings for a teacher (creator dashboard)
  - Response: JSON { teacher_id, listings }

---

## Discovery
- POST /discovery/suggest
  - Description: Suggest relevant listings for a query (AI-assisted fallback available).
  - Request: `DiscoverySuggestRequest` (query)
  - Response: `DiscoverySuggestResponse` (matches, reasoning)

- GET /discovery/listings
  - Description: Catalog of published listings (optional `limit` and `tag`).
  - Response: list of `ListingPublic`

- GET /discovery/listings/{listing_id}
  - Description: Course detail including video URLs, thumbnail, transcription, outcomes, average rating.
  - Response: `CourseDetailResponse`

---

## Sessions
- POST /sessions/start
  - Description: Start a session: verifies student/listing, checks balance, locks reserve amount, creates session row, creates escrow/payment intent (milestone-based) when possible.
  - Request: `SessionStartRequest` (student_id, listing_id, optional reserve_amount)
  - Response: `SessionStartResponse` (session_id, status, reserve_amount, transaction_id)

- POST /sessions/end
  - Description: End a session: compute duration/completion, compute final charge & refund, call Finternet settle/refund, update session and payments.
  - Request: `SessionEndRequest` (session_id, optional completion_percentage, engagement_metrics)
  - Response: `SessionEndBreakdown`

- GET /sessions/student/{student_id}
  - Description: List recent sessions for a student.

- GET /sessions/teacher/{teacher_id}
  - Description: List recent sessions for a teacher.

- GET /sessions/{session_id}/videos
  - Description: Return video URLs for an active session (MVP: public URLs).

---

## Payments
- GET /payments/by_session?session_id={session_id}
  - Description: Retrieve payment records (lock/settle/refund) for a session.
  - Response: JSON { session_id, payments }

---

## Reviews
- POST /reviews/submit
  - Description: Submit a session review after session ends; computes credibility + bonus (AI fallback heuristic) and stores review.
  - Request: `ReviewSubmitRequest` (session_id, student_id, rating, review_text)
  - Response: `ReviewSubmitResponse` (review_id, credibility_score, bonus_percentage, applied_bonus_amount)

---

## Teacher
- GET /teacher/profile/{teacher_id}
  - Description: Retrieve teacher profile and aggregated earnings & metrics (base earnings, bonus, avg rating/credibility).
  - Response: `TeacherProfileResponse`

- PUT /teacher/{teacher_id}
  - Description: Update teacher profile (name, bio)
  - Request: `TeacherUpdateRequest`
  - Response: `TeacherProfileResponse`

- GET /teacher/earnings/{teacher_id}
  - Description: Aggregated earnings for teacher (base + bonus).

- GET /teacher/quality/{teacher_id}
  - Description: Quality breakdown with reviews per session for teacher dashboard.

---

## Wallet
(See `app/routers/wallet.py` — common wallet helpers)
- POST /wallet/connect (or equivalent)
  - Description: Connect a user's wallet and return wallet address + balance.
- GET /wallet/balance?user_id={user_id}
  - Description: Retrieve wallet_balance for a user.

---

## Milestones & Escrow
- POST /milestones/intent
  - Description: Create a payment intent / escrow on Finternet for milestone-based payouts.
  - Request: `PaymentIntentRequest` (amount, currency, description, metadata)
  - Response: dict { intent_id, escrow_id, status, total_amount }

- GET /milestones/escrow/{intent_id}
  - Description: Retrieve escrow details (tries DB first, falls back to Finternet).
  - Response: `EscrowResponse`

- POST /milestones
  - Description: Create a milestone tied to an escrow and session (used in a loop as user engages content).
  - Request: `MilestoneCreateRequest` (escrow_id, session_id, index, description, amount, percentage)
  - Response: `MilestoneResponse`

- GET /milestones?escrow_id={escrow_id}&session_id={session_id}&limit=&offset=
  - Description: List milestones filtered by escrow or session.
  - Response: `MilestoneListResponse`

- GET /milestones/{milestone_id}
  - Description: Get milestone details.
  - Response: `MilestoneResponse`

- POST /milestones/{milestone_id}/proof
  - Description: Submit proof for a milestone (video URL). This automatically completes the milestone and triggers fund release to the teacher.
  - Request: `ProofSubmitRequest` (video_url, notes)
  - Response: `MilestoneCompleteResponse` (milestone_id, status, amount_released, finternet_tx_id)

- POST /milestones/{milestone_id}/complete
  - Description: Manual completion fallback (rarely used).
  - Response: `MilestoneCompleteResponse`

Notes:
- Proof submission expects a `video_url` (the watched content). When proof is submitted the router calls Finternet mock `submit_proof` and `complete_milestone`, then marks the milestone `completed` and stores `proof_data`.
- Finternet mock is in: [backend/app/services/finternet.py](app/services/finternet.py). Replace mocks with real HTTP calls when sandbox API is available.

---

## How to test (examples)
Start the server:

```bash
python server.py
```

Create a teacher and student using `/auth/register`, then create a session via `/sessions/start` (or use seeded data). Create a payment intent and milestones, then submit proof:

```bash
# create intent
curl -X POST http://localhost:8000/milestones/intent -H "Content-Type: application/json" \
  -d '{"amount":100.0, "currency":"USD"}'

# create milestone
curl -X POST http://localhost:8000/milestones -H "Content-Type: application/json" \
  -d '{"escrow_id":"escrow_...","session_id":"sess_...","index":0,"description":"Phase 1","amount":25,"percentage":25}'

# submit proof (auto-completes)
curl -X POST http://localhost:8000/milestones/{milestone_id}/proof -H "Content-Type: application/json" \
  -d '{"video_url":"https://example.com/watch/abc","notes":"User watched 100%"}'
```

---

## Implementation notes
- Schemas: [backend/app/schemas.py](app/schemas.py)
- DB helpers: [backend/app/supabase_client.py](app/supabase_client.py)
- Finternet mock with retries: [backend/app/services/finternet.py](app/services/finternet.py)
- Register new routes in: [backend/app/main.py](app/main.py)

If you want, I can:
- Add example Postman collection entries for these endpoints
- Generate OpenAPI extension/README with example payloads
- Add tests for core flows (start session → create intent → create milestone → submit proof)

---

Generated on: 2026-02-05
