# API Endpoints - Quick Reference Card

## Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| `POST` | `/auth/register` | Register new user | ❌ |
| `POST` | `/auth/login` | Login user | ❌ |

## Session Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| `POST` | `/sessions/start` | Create & lock session | ✅ |
| `POST` | `/sessions/end` | End session & settle payments | ✅ |
| `GET` | `/sessions/{session_id}` | Get session details | ✅ |
| `GET` | `/sessions/student/{student_id}` | List student's sessions | ✅ |
| `GET` | `/sessions/teacher/{teacher_id}` | List teacher's sessions | ✅ |
| `GET` | `/sessions/{session_id}/videos` | Get video URLs | ✅ |

## Payment Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| `GET` | `/payments/by_session?session_id={id}` | Get session payments | ✅ |

## Milestone & Escrow Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| `POST` | `/milestones/intent` | Create payment intent | ✅ |
| `GET` | `/milestones/escrow/{intent_id}` | Get escrow details | ✅ |
| `POST` | `/milestones` | Create milestone | ✅ |
| `GET` | `/milestones/{milestone_id}` | Get milestone details | ✅ |
| `GET` | `/milestones?session_id={id}` | List milestones by session | ✅ |
| `GET` | `/milestones?escrow_id={id}` | List milestones by escrow | ✅ |
| `POST` | `/milestones/{milestone_id}/proof` | Submit proof & auto-complete | ✅ |
| `POST` | `/milestones/{milestone_id}/complete` | Manual completion | ✅ |

## Wallet Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| `POST` | `/wallet/connect` | Connect wallet | ✅ |
| `GET` | `/wallet/balance` | Get wallet balance | ✅ |

## System Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/config` | Get public config | ❌ |

---

## Request/Response Structures

### SessionStartRequest
```json
{
  "student_id": "user_1",
  "listing_id": "session1",
  "reserve_amount": 45.00
}
```

### SessionStartResponse
```json
{
  "session_id": "sess_a1b2c3d4e5f6",
  "status": "active",
  "reserve_amount": 45.00,
  "transaction_id": "tx_abc123def456"
}
```

### SessionEndRequest
```json
{
  "session_id": "sess_a1b2c3d4e5f6",
  "completion_percentage": 95,
  "engagement_metrics": {
    "videoProgress": 95,
    "elapsedTime": 5400
  }
}
```

### SessionEndBreakdown
```json
{
  "session_id": "sess_a1b2c3d4e5f6",
  "listing_id": "session1",
  "teacher_id": "user_2",
  "student_id": "user_1",
  "start_time": "2024-02-05T10:30:00Z",
  "end_time": "2024-02-05T11:45:00Z",
  "duration_min": 75.5,
  "completion_percentage": 95,
  "reserve_amount": 45.00,
  "final_amount_charged": 37.50,
  "refund_amount": 7.50,
  "settle_transaction_id": "tx_settle123"
}
```

### PaymentIntentRequest
```json
{
  "amount": 45.0,
  "currency": "USD",
  "description": "Session payment",
  "metadata": {
    "session_id": "sess_abc123",
    "student_id": "user_1"
  }
}
```

### PaymentIntentResponse
```json
{
  "intent_id": "intent_xyz789",
  "escrow_id": "escrow_abc123",
  "status": "active",
  "total_amount": 45.0
}
```

### EscrowResponse
```json
{
  "id": "escrow_abc123",
  "session_id": "sess_a1b2c3d4e5f6",
  "finternet_intent_id": "intent_xyz",
  "total_amount": 45.00,
  "locked_amount": 45.00,
  "status": "active",
  "created_at": "2024-02-05T10:30:00Z"
}
```

### MilestoneCreateRequest
```json
{
  "escrow_id": "escrow_abc123",
  "session_id": "sess_a1b2c3d4e5f6",
  "index": 0,
  "description": "Phase 1",
  "amount": 22.50,
  "percentage": 50
}
```

### MilestoneResponse
```json
{
  "id": "milestone_123",
  "escrow_id": "escrow_abc123",
  "session_id": "sess_a1b2c3d4e5f6",
  "index": 0,
  "description": "Phase 1",
  "amount": 22.50,
  "percentage": 50,
  "status": "pending",
  "proof_data": null,
  "created_at": "2024-02-05T10:30:00Z"
}
```

### ProofSubmitRequest
```json
{
  "video_url": "https://example.com/watch/abc123",
  "notes": "Completed 95% of content"
}
```

### MilestoneCompleteResponse
```json
{
  "milestone_id": "milestone_123",
  "status": "completed",
  "amount_released": 22.50,
  "finternet_tx_id": "tx_release123"
}
```

---

## HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created |
| `400` | Bad Request | Invalid parameters, wallet not connected |
| `401` | Unauthorized | Missing/invalid auth token |
| `402` | Payment Required | Insufficient balance |
| `404` | Not Found | Session/user/milestone not found |
| `500` | Server Error | Internal server error |

---

## Error Response Format

```json
{
  "error": {
    "message": "Descriptive error message",
    "code": "ERROR_CODE"
  }
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| `STUDENT_NOT_FOUND` | Student ID doesn't exist |
| `LISTING_NOT_FOUND` | Listing ID doesn't exist |
| `WALLET_NOT_CONNECTED` | Student's wallet not connected |
| `INSUFFICIENT_BALANCE` | Student has insufficient funds |
| `SESSION_NOT_FOUND` | Session ID doesn't exist |
| `SESSION_NOT_ACTIVE` | Session is not in active state |
| `ESCROW_NOT_FOUND` | Escrow ID doesn't exist |
| `MILESTONE_NOT_FOUND` | Milestone ID doesn't exist |
| `INTENT_FAILED` | Payment intent creation failed |

---

## Complete Session Flow

```
[Start Session]
    ↓
POST /sessions/start
    ↓
[Get session_id, transaction_id]
    ↓
[Create Payment Intent]
    ↓
POST /milestones/intent
    ↓
[Get intent_id, escrow_id]
    ↓
[Create Milestones]
    ↓
POST /milestones (repeat as needed)
    ↓
[Get milestone_id]
    ↓
[User watches content]
    ↓
[End Session]
    ↓
POST /sessions/end
    ↓
[Get final breakdown]
    ↓
[Submit Milestone Proofs]
    ↓
POST /milestones/{id}/proof (repeat)
    ↓
[Verify Payments]
    ↓
GET /payments/by_session?session_id={id}
```

---

## Environment Variables for Postman

```
BASE_URL = http://localhost:8000
ACCESS_TOKEN = (from login)
STUDENT_ID = user_1
TEACHER_ID = user_2
SESSION_ID = (from start session)
LISTING_ID = session1
INTENT_ID = (from create intent)
ESCROW_ID = (from create intent)
MILESTONE_ID = (from create milestone)
RESERVE_AMOUNT = 45.0
VIDEO_URL = https://example.com/video
```

---

## Quick Testing Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "role": "student"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }'
```

### Start Session
```bash
curl -X POST http://localhost:8000/sessions/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "user_1",
    "listing_id": "session1",
    "reserve_amount": 45.00
  }'
```

### End Session
```bash
curl -X POST http://localhost:8000/sessions/end \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123",
    "completion_percentage": 95,
    "engagement_metrics": {"videoProgress": 95}
  }'
```

### Create Intent
```bash
curl -X POST http://localhost:8000/milestones/intent \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45.0,
    "currency": "USD",
    "description": "Session payment"
  }'
```

### Submit Proof
```bash
curl -X POST http://localhost:8000/milestones/milestone_123/proof \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video",
    "notes": "Completed 95%"
  }'
```

---

## Notes

- All timestamps are in **ISO 8601 format** (e.g., `2024-02-05T10:30:00Z`)
- Amounts are in **USD** currency
- Session IDs start with `sess_`
- Transaction IDs start with `tx_`
- Milestone IDs start with `milestone_`
- All monetary amounts use **2 decimal places**
- Percentages range from **0-100**

---

**Tip**: Use this card as a bookmark in your browser for quick reference while testing!

**Last Updated**: February 5, 2026
