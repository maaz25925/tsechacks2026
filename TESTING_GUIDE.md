# API Integration Testing Guide

## Test Environment Setup

### Prerequisites
```bash
# Backend dependencies
cd backend
uv install

# Frontend dependencies
cd ../frontend
npm install
```

### Start Backend
```bash
cd backend
python server.py
# Server runs on http://localhost:8000
```

### Start Frontend (Vite)
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

## Test Scenarios

### Scenario 1: Complete Session Flow (Happy Path)

**Objective**: Verify the complete flow from session start to completion

**Steps**:
1. Login as student
   - Navigate to `/auth`
   - Enter credentials: email: `alice@example.com`, password: `password123`
   - Should show dashboard

2. Browse sessions
   - Navigate to `/discover`
   - Click on a session card
   - Should show session detail page

3. Lock funds and start
   - Click "Lock Funds & Start" button
   - **Expected**:
     - Button shows "Locking Funds..."
     - Success alert appears with session_id
     - Payment intent confirmation shows
     - Auto-navigates to /active-session/{session_id}

4. Watch video
   - Video player loads
   - Click play
   - Observe progress bar updating
   - **Expected**:
     - Timer increments every second
     - Cost increases: timer_seconds/60 * price_per_minute
     - Video progress shown as percentage

5. End session
   - Watch video to ~90% completion
   - Click "End Session" button
   - **Expected**:
     - Button shows "Ending..."
     - Buttons disabled during process
     - Redirects to /summary/{session_id}

**Expected Results**:
- Session created with status "active"
- Payment intent created with correct amount
- Session ends with correct final charge calculation
- Milestones submitted successfully

**Validation**:
```bash
# Check backend logs for:
# - Session created log entry
# - Payment intent created log entry
# - Session ended with calculated costs
```

### Scenario 2: Insufficient Balance Error

**Objective**: Verify error handling when student has insufficient funds

**Steps**:
1. Create a test student with balance < session price
2. Navigate to session detail
3. Try to lock funds
4. **Expected**: 
   - Error alert: "Insufficient balance"
   - Balance shown vs required amount
   - Button remains clickable for retry

**Validation**:
```bash
# Backend should return 402 status code
curl -X POST http://localhost:8000/sessions/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"student_id": "low_balance_user", "listing_id": "session1", "reserve_amount": 1000}'
# Response: 402 - Insufficient balance
```

### Scenario 3: Session with Multiple Milestones

**Objective**: Verify milestone creation and proof submission

**Steps**:
1. Start a session normally
2. In backend, create milestones:
   ```bash
   curl -X POST http://localhost:8000/milestones \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "escrow_id": "escrow_xyz",
       "session_id": "sess_abc",
       "index": 0,
       "description": "Phase 1",
       "amount": 15,
       "percentage": 33
     }'
   ```
3. Complete session
4. **Expected**:
   - Milestones automatically discovered
   - Proofs submitted for each milestone
   - Milestone status changes to "completed"

### Scenario 4: Error Recovery and Retry

**Objective**: Verify application handles network errors gracefully

**Steps**:
1. Stop backend server
2. Try to start a session
3. **Expected**:
   - Error message displayed: "Failed to lock funds..."
   - Button remains enabled
   - Can retry after backend restarts

4. Restart backend
5. Click button again
   - Should succeed

### Scenario 5: Session Timer Accuracy

**Objective**: Verify timer and cost calculations are accurate

**Steps**:
1. Start a session
2. Note start time
3. Wait exactly 1 minute
4. **Expected**:
   - Timer shows 00:01
   - Cost = 1 * session.pricePerMinute
5. Wait 5 minutes total
6. **Expected**:
   - Timer shows 00:05
   - Cost = 5 * session.pricePerMinute

**Validation**:
```javascript
// In browser console
// Check elapsed time updates
setInterval(() => {
  console.log('Timer element:', 
    document.querySelector('.timer-value')?.textContent
  );
}, 5000);
```

## API Testing (Curl)

### Test 1: Register Student
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123",
    "name": "Test User",
    "role": "student"
  }'
```

**Expected Response**:
```json
{
  "user_id": "user_xyz",
  "email": "testuser@example.com",
  "role": "student",
  "access_token": "eyJ..."
}
```

### Test 2: Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }'
```

### Test 3: Start Session
```bash
curl -X POST http://localhost:8000/sessions/start \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "user_1",
    "listing_id": "session1",
    "reserve_amount": 45.00
  }'
```

**Expected Response**:
```json
{
  "session_id": "sess_a1b2c3",
  "status": "active",
  "reserve_amount": 45.0,
  "transaction_id": "tx_abc123"
}
```

### Test 4: Create Payment Intent
```bash
curl -X POST http://localhost:8000/milestones/intent \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45.0,
    "currency": "USD",
    "description": "Session payment",
    "metadata": {"session_id": "sess_a1b2c3"}
  }'
```

**Expected Response**:
```json
{
  "intent_id": "intent_xyz",
  "escrow_id": "escrow_abc",
  "status": "active",
  "total_amount": 45.0
}
```

### Test 5: End Session
```bash
curl -X POST http://localhost:8000/sessions/end \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_a1b2c3",
    "completion_percentage": 95,
    "engagement_metrics": {
      "videoProgress": 95,
      "elapsedTime": 5400
    }
  }'
```

**Expected Response**:
```json
{
  "session_id": "sess_a1b2c3",
  "listing_id": "session1",
  "teacher_id": "user_2",
  "student_id": "user_1",
  "start_time": "2024-02-05T10:30:00Z",
  "end_time": "2024-02-05T11:45:00Z",
  "duration_min": 75.5,
  "completion_percentage": 95,
  "reserve_amount": 45.0,
  "final_amount_charged": 37.5,
  "refund_amount": 7.5,
  "settle_transaction_id": "tx_settle123"
}
```

### Test 6: Submit Milestone Proof
```bash
curl -X POST http://localhost:8000/milestones/milestone_123/proof \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video",
    "notes": "Completed 95% of content"
  }'
```

**Expected Response**:
```json
{
  "milestone_id": "milestone_123",
  "status": "completed",
  "amount_released": 15.0,
  "finternet_tx_id": "tx_release123"
}
```

## Frontend Testing Checklist

### Page Navigation
- [ ] SessionDetail page loads
- [ ] ActiveSession page loads
- [ ] Summary page loads
- [ ] Navigation between pages works
- [ ] Back button works

### SessionDetail Component
- [ ] Session title displays
- [ ] Instructor info displays
- [ ] Price per minute displays correctly
- [ ] Learning objectives list displays
- [ ] "Lock Funds & Start" button visible
- [ ] Wallet status component displays
- [ ] Estimated cost calculated correctly

### Fund Locking Flow
- [ ] Click "Lock Funds & Start"
- [ ] Loading state shows "Locking Funds..."
- [ ] Request sent with correct payload
- [ ] Success alert appears
- [ ] Alert shows session_id
- [ ] Alert shows transaction_id
- [ ] Payment intent confirmation appears
- [ ] Navigation to /active-session occurs
- [ ] All form data cleared

### ActiveSession Component
- [ ] Video player loads
- [ ] Video plays on click
- [ ] Play/pause controls work
- [ ] Full screen works
- [ ] Progress bar updates

### SessionTimer Component
- [ ] Timer displays 00:00 on start
- [ ] Timer increments each second
- [ ] Format is HH:MM:SS (with padding)
- [ ] Cost displays correctly
- [ ] Cost = elapsed_minutes * pricePerMinute
- [ ] Pause button toggles pause state
- [ ] Resume button toggles resume state
- [ ] End session button triggers callback
- [ ] Buttons disabled during session end

### Error Handling
- [ ] Invalid session shows error
- [ ] Network error shows alert
- [ ] Insufficient balance shows error
- [ ] API errors handled gracefully
- [ ] Error dismiss/retry works

### State Management
- [ ] Session data persists while active
- [ ] Timer state updates don't cause re-renders
- [ ] Cost calculation updates correctly
- [ ] Error state clears on retry

## Browser DevTools Testing

### Console Checks
```javascript
// Check API calls in Network tab
// Filter: /sessions, /milestones

// Check for errors
// Filter: Error, Failed

// Monitor state changes
// SessionDetail: sessionData, intentData, error, isLocking
// ActiveSession: error, isEnding, elapsedTime, videoProgress
```

### Network Tab
1. Start session
   - Look for POST /sessions/start
   - Status: 200 OK
   - Response: SessionStartResponse

2. Create intent
   - Look for POST /milestones/intent
   - Status: 200 OK
   - Response: PaymentIntentResponse

3. End session
   - Look for POST /sessions/end
   - Status: 200 OK
   - Response: SessionEndBreakdown

4. List milestones
   - Look for GET /milestones
   - Status: 200 OK
   - Response: {milestones: [...]}

5. Submit proofs
   - Look for POST /milestones/{id}/proof
   - Status: 200 OK
   - Response: MilestoneCompleteResponse

### Errors Expected
- 404: Session not found
- 402: Insufficient balance
- 400: Invalid request
- 500: Server error

## Performance Testing

### Metrics to Monitor
1. **API Response Time**
   - session/start: < 500ms
   - sessions/end: < 500ms
   - milestones/intent: < 250ms
   - milestones/{id}/proof: < 300ms

2. **Component Rendering**
   - SessionDetail initial: < 100ms
   - ActiveSession initial: < 150ms
   - Timer updates: < 50ms

3. **Memory Usage**
   - Session active: < 10MB increase
   - After session: memory released

## Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Tab order is logical
- [ ] Buttons have focus indicators
- [ ] Error messages associated with inputs
- [ ] Color contrast adequate
- [ ] Labels present for all inputs

## Final Sign-Off

Before deployment, verify:
- [ ] All happy path scenarios pass
- [ ] All error scenarios handled
- [ ] API response times acceptable
- [ ] No console errors
- [ ] No network request failures
- [ ] Mobile responsive
- [ ] Browser compatibility verified
