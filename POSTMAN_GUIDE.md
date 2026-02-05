# Postman API Testing Guide

## Overview

This guide provides instructions for importing and using the Murph Backend API collection in Postman for comprehensive API testing.

---

## 📦 Files Included

### Collection Files
- **`Murph_API_Postman.postman_collection.json`** - Complete API collection with all endpoints and example requests

### Environment Files
- **`Murph_API_Development.postman_environment.json`** - Development environment (localhost:8000)
- **`Murph_API_Staging.postman_environment.json`** - Staging environment
- **`Murph_API_Production.postman_environment.json`** - Production environment

---

## 🚀 Getting Started

### Step 1: Import the Collection

1. Open **Postman** (desktop app or web)
2. Click **"Import"** button (top left)
3. Select **"File"** tab
4. Choose `Murph_API_Postman.postman_collection.json`
5. Click **"Import"**

**Result**: You'll see "Murph Backend API" in your collections on the left sidebar

### Step 2: Import an Environment

1. Click the **"Environments"** icon (left sidebar)
2. Click **"Import"**
3. Choose the environment file:
   - `Murph_API_Development.postman_environment.json` (for local testing)
   - `Murph_API_Staging.postman_environment.json` (for staging)
   - `Murph_API_Production.postman_environment.json` (for production)
4. Click **"Import"**

### Step 3: Select Your Environment

1. In the top right, find the **Environment dropdown** (currently shows "No Environment")
2. Click and select your environment (e.g., "Murph Backend - Development")

**Tip**: The environment selector shows which environment you're currently using

---

## 📋 Collection Structure

The collection is organized into logical folders:

```
Murph Backend API
├── Authentication
│   ├── Register
│   └── Login
├── Sessions
│   ├── Start Session
│   ├── End Session
│   ├── Get Session Details
│   ├── Get Student Sessions
│   ├── Get Teacher Sessions
│   └── Get Session Videos
├── Payments
│   └── Get Session Payments
├── Milestones
│   ├── Create Payment Intent
│   ├── Get Escrow Details
│   ├── Create Milestone
│   ├── Get Milestone Details
│   ├── List Milestones by Session
│   ├── List Milestones by Escrow
│   ├── Submit Milestone Proof
│   └── Complete Milestone (Manual)
├── Wallet
│   ├── Connect Wallet
│   └── Get Wallet Balance
└── Health & Config
    ├── Health Check
    └── Get Config
```

---

## 🔑 Authentication Flow

### Step 1: Register a New User

1. Go to **Authentication → Register**
2. Modify the request body with your details:
   ```json
   {
     "email": "testuser@example.com",
     "password": "password123",
     "name": "Test User",
     "role": "student",
     "bio": "Learning new skills"
   }
   ```
3. Click **Send**
4. Copy the `access_token` from the response

### Step 2: Set the Access Token

1. Go to **Environments** 
2. Select your active environment
3. Find the `ACCESS_TOKEN` variable
4. Paste the token you copied in the **"Current Value"** column
5. Click **Save** (Ctrl+S)

### Alternative: Login with Existing User

1. Go to **Authentication → Login**
2. Use existing credentials:
   ```json
   {
     "email": "alice@example.com",
     "password": "password123"
   }
   ```
3. Click **Send**
4. Copy the `access_token` and set it in your environment (steps 1-5 above)

---

## 🎬 Complete Testing Workflow

### Scenario: Start a Session and Complete with Milestones

#### Phase 1: Initial Setup

1. **Health Check**
   - Go to **Health & Config → Health Check**
   - Click **Send**
   - Verify the server is running

2. **Register/Login**
   - Register or login as a student
   - Copy and set the `ACCESS_TOKEN` in your environment

#### Phase 2: Start a Session

1. **Start Session**
   - Go to **Sessions → Start Session**
   - The request body uses:
     - `student_id`: {{STUDENT_ID}} from environment
     - `listing_id`: {{LISTING_ID}} from environment
     - `reserve_amount`: {{RESERVE_AMOUNT}} from environment
   - Click **Send**
   - **Expected Response**: 
     ```json
     {
       "session_id": "sess_abc123...",
       "status": "active",
       "reserve_amount": 45.0,
       "transaction_id": "tx_xyz..."
     }
     ```
   - Copy the `session_id` and update `SESSION_ID` in your environment

#### Phase 3: Create Payment Intent

1. **Create Payment Intent**
   - Go to **Milestones → Create Payment Intent**
   - Click **Send**
   - **Expected Response**:
     ```json
     {
       "intent_id": "intent_xyz...",
       "escrow_id": "escrow_abc...",
       "status": "active",
       "total_amount": 45.0
     }
     ```
   - Copy `intent_id` and `escrow_id` into your environment variables

#### Phase 4: Create Milestones

1. **Create First Milestone**
   - Go to **Milestones → Create Milestone**
   - Update body with your `escrow_id` and `session_id`
   - Modify amount and percentage as needed:
     ```json
     {
       "escrow_id": "{{ESCROW_ID}}",
       "session_id": "{{SESSION_ID}}",
       "index": 0,
       "description": "Phase 1 - Introduction",
       "amount": 22.50,
       "percentage": 50
     }
     ```
   - Click **Send**
   - Copy the returned `milestone_id`

#### Phase 5: Simulate Session Completion

1. **Get Session Milestones**
   - Go to **Milestones → List Milestones by Session**
   - Ensure `session_id` parameter is set
   - Click **Send**
   - Verify milestones are listed with status "pending"

2. **Submit Milestone Proof**
   - Go to **Milestones → Submit Milestone Proof**
   - Update the URL with your `milestone_id`:
     - From: `/milestones/milestone_123/proof`
     - To: `/milestones/{{MILESTONE_ID}}/proof`
   - Update body with your video URL:
     ```json
     {
       "video_url": "https://your-video-url.com/video",
       "notes": "User completed 95% of content"
     }
     ```
   - Click **Send**
   - **Expected Response**:
     ```json
     {
       "milestone_id": "milestone_123",
       "status": "completed",
       "amount_released": 22.50,
       "finternet_tx_id": "tx_release123"
     }
     ```

#### Phase 6: End Session

1. **End Session**
   - Go to **Sessions → End Session**
   - Update body with your session details:
     ```json
     {
       "session_id": "{{SESSION_ID}}",
       "completion_percentage": 95,
       "engagement_metrics": {
         "videoProgress": 95,
         "elapsedTime": 5400,
         "timestamp": "2024-02-05T11:45:00Z"
       }
     }
     ```
   - Click **Send**
   - **Expected Response**: Session breakdown with final charges

#### Phase 7: Verify Payments

1. **Get Session Payments**
   - Go to **Payments → Get Session Payments**
   - Update query parameter with your `session_id`
   - Click **Send**
   - Verify all payment records (lock, settle, refund)

---

## 🔧 Environment Variables

### Development Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `BASE_URL` | `http://localhost:8000` | Backend API base URL |
| `ACCESS_TOKEN` | (empty - fill after login) | JWT authentication token |
| `STUDENT_ID` | `user_1` | Test student ID |
| `TEACHER_ID` | `user_2` | Test teacher ID |
| `SESSION_ID` | `sess_a1b2c3d4e5f6` | Active session ID |
| `LISTING_ID` | `session1` | Listing/course ID |
| `INTENT_ID` | `intent_xyz789` | Payment intent ID |
| `ESCROW_ID` | `escrow_abc123` | Escrow account ID |
| `MILESTONE_ID` | `milestone_123` | Milestone ID |
| `RESERVE_AMOUNT` | `45.0` | Reserve amount for session |
| `VIDEO_URL` | `https://example.com/watch/abc123` | Video URL for proof |

### Switching Environments

To change environments:
1. Top right corner of Postman
2. Click environment dropdown
3. Select desired environment
4. All variables automatically update

---

## 📝 Common Use Cases

### Use Case 1: Test Authentication

```
1. Run: Authentication → Register
2. Copy access_token
3. Set environment variable: ACCESS_TOKEN
4. Verify: Health → Health Check (will use auth token)
```

### Use Case 2: Test Complete Session Flow

```
1. Health Check
2. Login (set ACCESS_TOKEN)
3. Start Session (copy session_id)
4. Create Payment Intent (copy intent_id, escrow_id)
5. Create Milestone
6. Submit Proof
7. End Session
8. Get Payments
```

### Use Case 3: Test Error Scenarios

#### Insufficient Balance
```json
// In Start Session, set reserve_amount to a very high number
{
  "student_id": "user_1",
  "listing_id": "session1",
  "reserve_amount": 999999.99
}
// Expected: 402 - Insufficient balance
```

#### Wallet Not Connected
```
// Try to start session without wallet
// Expected: 400 - Wallet not connected
```

#### Session Not Found
```
// In End Session, use invalid session_id: "invalid_session"
// Expected: 404 - Session not found
```

---

## 💡 Tips & Tricks

### Auto-save Variables from Response

1. Go to a request (e.g., Start Session)
2. Click **"Tests"** tab (right side)
3. Add this script:
   ```javascript
   if (pm.response.code === 200) {
       const response = pm.response.json();
       pm.environment.set("SESSION_ID", response.session_id);
       pm.environment.set("TRANSACTION_ID", response.transaction_id);
   }
   ```
4. Now when you send the request, variables auto-update

### View Request History

- Click **"History"** tab (left sidebar)
- All previous requests and responses
- Useful for debugging

### Use Collections Generator

- Export collection
- Share with team
- Import in their Postman
- Everyone has same API structure

### Pre-request Scripts

Add common setup before requests:
1. Click **"Pre-request Script"** tab
2. Example: Validate environment variables
   ```javascript
   if (!pm.environment.get("ACCESS_TOKEN")) {
       console.error("ACCESS_TOKEN not set!");
   }
   ```

---

## 🧪 Testing Checklist

### Prerequisites
- [ ] Postman installed or using web version
- [ ] Backend server running (localhost:8000)
- [ ] Collection imported
- [ ] Environment imported and selected

### Authentication Tests
- [ ] Health Check returns 200
- [ ] Register creates new user
- [ ] Login returns access_token
- [ ] Invalid credentials returns error

### Session Tests
- [ ] Start Session locks funds
- [ ] Get Session Details returns correct info
- [ ] Get Student Sessions lists sessions
- [ ] End Session calculates charges
- [ ] Insufficient balance returns 402

### Milestone Tests
- [ ] Create Payment Intent establishes escrow
- [ ] Create Milestone stores milestone data
- [ ] List Milestones shows all milestones
- [ ] Submit Proof completes milestone
- [ ] Get Escrow returns correct details

### Payment Tests
- [ ] Get Session Payments lists all transactions
- [ ] Payment types (lock, settle, refund)
- [ ] Transaction IDs tracked correctly

---

## 🐛 Troubleshooting

### Issue: "No Environment Selected"
**Solution**: Select environment from dropdown (top right)

### Issue: "Cannot GET /sessions/start"
**Solution**: Ensure BASE_URL is correct in environment (should be http://localhost:8000)

### Issue: 401 Unauthorized
**Solution**: 
- Ensure ACCESS_TOKEN is set in environment
- Token may have expired - login again
- Check token value doesn't have extra spaces

### Issue: 404 Not Found
**Solution**:
- Verify session_id/milestone_id exists
- Check variables are correctly interpolated: {{VARIABLE}}
- Ensure IDs match what was returned from previous requests

### Issue: CORS Error
**Solution**:
- Enable CORS on backend
- Check allowed_origins in backend config
- Frontend should be running on allowed origin

### Issue: Connection Refused
**Solution**:
- Ensure backend server is running: `python server.py`
- Verify BASE_URL matches your backend URL
- Check if port 8000 is in use

---

## 📚 Additional Resources

- [Postman Documentation](https://learning.postman.com/)
- [API Routes Documentation](./backend/API_ROUTES.md)
- [Backend Setup Guide](./backend/README.md)
- [Frontend Integration Guide](./frontend/INTEGRATION_GUIDE.md)

---

## 🔗 Quick Links

### For Development
- Collection: `Murph_API_Postman.postman_collection.json`
- Environment: `Murph_API_Development.postman_environment.json`
- Backend URL: `http://localhost:8000`

### For Staging
- Collection: Same as above
- Environment: `Murph_API_Staging.postman_environment.json`
- Backend URL: `https://staging-api.murph.example.com`

### For Production
- Collection: Same as above
- Environment: `Murph_API_Production.postman_environment.json`
- Backend URL: `https://api.murph.example.com`

---

## 📞 Support

For issues or questions:
1. Check this guide's Troubleshooting section
2. Review backend API_ROUTES.md
3. Check server logs: `python server.py`
4. Check Postman console: Cmd+Alt+C (Mac) or Ctrl+Alt+C (Windows)

---

**Last Updated**: February 5, 2026
**Postman Version**: v11.0.0+
**Status**: ✅ Ready for Testing
