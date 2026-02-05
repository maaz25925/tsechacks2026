# API Integration - Visual Reference

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STUDENT SESSION FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

PHASE 1: DISCOVERY & SELECTION
┌──────────────┐
│   Discover   │  Browse available sessions
│   Sessions   │  (Discover.jsx → mockSessions)
└──────────────┘
       │
       ↓
┌──────────────────────┐
│ SessionDetail.jsx    │  Display session info
│ - Title              │  - Price: $0.50/min
│ - Instructor         │  - Duration: 90 min
│ - Learning goals     │  - Est. cost: $45
└──────────────────────┘
       │
       ↓
   [Lock Funds]  ← User clicks button

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 2: FUND LOCKING
┌──────────────────────────────────┐
│   Frontend                       │
│ - Check user authentication      │
│ - Validate reserves amount       │
└──────────────────────────────────┘
       │
       ├──→ sessionService.startSession()
       │
       ↓
┌──────────────────────────────────┐
│   Backend: /sessions/start        │
│ - Verify student exists          │
│ - Check wallet balance           │
│ - Lock funds via Finternet       │
│ - Create session record          │
│ - Return session_id & tx_id      │
└──────────────────────────────────┘
       │
       ├──→ Response: {
       │       session_id: "sess_abc123",
       │       status: "active",
       │       reserve_amount: 45.00,
       │       transaction_id: "tx_xyz..."
       │    }
       │
       ├──→ milestonesService.createPaymentIntent()
       │
       ↓
┌──────────────────────────────────┐
│   Backend: /milestones/intent     │
│ - Create payment intent          │
│ - Setup escrow account           │
│ - Return intent details          │
└──────────────────────────────────┘
       │
       ├──→ Response: {
       │       intent_id: "intent_xyz",
       │       escrow_id: "escrow_abc",
       │       status: "active",
       │       total_amount: 45.00
       │    }
       │
       ↓
┌──────────────────────────────────┐
│   Frontend: SessionDetail.jsx     │
│ - Show success alert             │
│ - Display transaction IDs        │
│ - Show payment intent info       │
└──────────────────────────────────┘
       │
       ↓
   [Navigate to ActiveSession]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 3: ACTIVE SESSION
┌──────────────────────────────────┐
│   ActiveSession.jsx              │
│ - Video player                   │
│ - SessionTimer component         │
│ - Progress tracking              │
└──────────────────────────────────┘
       │
       ├─→ ReactPlayer loads video
       │
       ├─→ Timer starts:
       │   - Elapsed: 00:00
       │   - Cost: $0.00
       │
       ├─→ Video plays
       │   - User watches content
       │   - Progress tracked: 0% → 100%
       │   - Timer increments: 00:00 → XX:XX
       │   - Cost updates: $0.00 → $45.00
       │
       ↓
   [User clicks "End Session"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 4: SESSION COMPLETION
┌──────────────────────────────────┐
│   Frontend: ActiveSession.jsx     │
│ - Collect completion %           │
│ - Gather engagement metrics      │
│ - Disable UI during end          │
└──────────────────────────────────┘
       │
       ├──→ sessionService.endSession({
       │       sessionId: "sess_abc123",
       │       completionPercentage: 95,
       │       engagementMetrics: {...}
       │    })
       │
       ↓
┌──────────────────────────────────┐
│   Backend: /sessions/end          │
│ - Calculate session duration     │
│ - Compute completion %           │
│ - Calculate final charge         │
│ - Calculate refund               │
│ - Settle to teacher              │
│ - Refund student                 │
│ - Update session status          │
└──────────────────────────────────┘
       │
       ├──→ Response: {
       │       session_id: "sess_abc123",
       │       duration_min: 75.5,
       │       final_charge: 37.50,
       │       refund_amount: 7.50,
       │       settle_tx_id: "tx_settle..."
       │    }
       │
       ├──→ milestonesService.listMilestones({
       │       sessionId: "sess_abc123"
       │    })
       │
       ↓
┌──────────────────────────────────┐
│   Backend: GET /milestones        │
│ - Find milestones for session    │
│ - Return pending milestones      │
└──────────────────────────────────┘
       │
       ├──→ For each milestone:
       │    milestonesService.submitProof(
       │       milestone_id,
       │       { videoUrl, notes }
       │    )
       │
       ↓
┌──────────────────────────────────┐
│   Backend: /milestones/{id}/proof │
│ - Verify proof content           │
│ - Mark milestone completed       │
│ - Release funds to teacher       │
│ - Return completion response     │
└──────────────────────────────────┘
       │
       ↓
┌──────────────────────────────────┐
│   Frontend: Summary.jsx          │
│ - Display breakdown              │
│ - Show earnings/charges          │
│ - Option to rate/review          │
└──────────────────────────────────┘

```

## Service Interaction Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     Frontend Application                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────┐  ┌──────────────────────────┐   │
│  │    SessionDetail.jsx     │  │  ActiveSession.jsx       │   │
│  ├──────────────────────────┤  ├──────────────────────────┤   │
│  │ - Display session info   │  │ - Video player          │   │
│  │ - Lock funds button      │  │ - Session timer         │   │
│  │ - Show confirmation      │  │ - End session button    │   │
│  └────────────┬─────────────┘  └────────────┬────────────┘   │
│               │                             │                 │
│               └─────────────┬───────────────┘                 │
│                             │                                 │
│                    ┌────────▼──────────┐                      │
│                    │  useAuth() Hook   │                      │
│                    └────────┬──────────┘                      │
│                             │                                 │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │       Services Layer (API Clients)                     │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │                                                       │ │
│  │  ┌──────────────────────┐  ┌──────────────────────┐ │ │
│  │  │  sessionService.js   │  │ milestonesService.js│ │ │
│  │  ├──────────────────────┤  ├──────────────────────┤ │ │
│  │  │ - startSession()     │  │ - createIntent()    │ │ │
│  │  │ - endSession()       │  │ - getEscrow()       │ │ │
│  │  │ - getSession()       │  │ - createMilestone() │ │ │
│  │  │ - getSessionVideos() │  │ - listMilestones()  │ │ │
│  │  │ - getPayments()      │  │ - submitProof()     │ │ │
│  │  └──────────┬───────────┘  └────────┬────────────┘ │ │
│  │             │                       │              │ │
│  │             └───────────┬───────────┘              │ │
│  │                         │                          │ │
│  │                  ┌──────▼──────┐                   │ │
│  │                  │  axios API  │                   │ │
│  │                  └──────┬──────┘                   │ │
│  │                         │                          │ │
│  └─────────────────────────┼──────────────────────────┘ │
│                            │                            │
└────────────────────────────┼────────────────────────────┘
                             │
                      HTTP Requests
                             │
            ┌────────────────▼────────────────┐
            │   Backend API Server            │
            │   (localhost:8000)              │
            ├─────────────────────────────────┤
            │                                 │
            │ Routes:                         │
            │ - POST /sessions/start          │
            │ - POST /sessions/end            │
            │ - GET /sessions/*               │
            │ - POST /milestones/intent       │
            │ - POST /milestones              │
            │ - POST /milestones/*/proof      │
            │                                 │
            └────────────┬────────────────────┘
                         │
                    Database & Finternet
                         │
            ┌────────────▼────────────────┐
            │   Finternet (Payment Mock)  │
            ├─────────────────────────────┤
            │ - lock_funds()              │
            │ - settle()                  │
            │ - refund()                  │
            │ - create_payment_intent()   │
            │ - submit_proof()            │
            │ - complete_milestone()      │
            └─────────────────────────────┘
```

## State Flow Diagram

```
SessionDetail Component State
────────────────────────────

Initial:    entered = false
            isLocking = false
            error = null
            sessionData = null
            intentData = null

User clicks "Lock Funds & Start":
    ↓
    isLocking = true
    
    API Call 1: sessionService.startSession()
    ↓
    Success:
        sessionData = { session_id, status, reserve_amount, tx_id }
        
        API Call 2: milestonesService.createPaymentIntent()
        ↓
        Success:
            intentData = { intent_id, escrow_id, status, total }
            isLocking = false
            Auto-navigate to /active-session/{session_id}
            
        Failure:
            error = "Payment intent creation failed"
            isLocking = false
            
    Failure:
        error = "Failed to lock funds"
        isLocking = false


ActiveSession Component State
─────────────────────────────

Initial:    videoProgress = 0
            isEnding = false
            error = null
            elapsedTime = 0

Video plays:
    ↓
    videoProgress = 0 → 100 (from ReactPlayer)
    SessionTimer increments:
        elapsedTime = 0, 1, 2, 3, ... (seconds)
        estimatedCost = (elapsedTime / 60) * pricePerMinute

User clicks "End Session":
    ↓
    isEnding = true
    
    API Call 1: sessionService.endSession({
        sessionId, completionPercentage, engagementMetrics
    })
    ↓
    Success:
        API Call 2: milestonesService.listMilestones()
        ↓
        Success:
            For each milestone:
                API Call 3: milestonesService.submitProof()
                ↓
                (Continue or fail gracefully)
            
            isEnding = false
            Auto-navigate to /summary/{sessionId}
            
        Failure:
            error = "Failed to list milestones"
            isEnding = false
            
    Failure:
        error = "Failed to end session"
        isEnding = false


SessionTimer Component State
────────────────────────────

Initial:    elapsed = 0
            isPaused = false

useEffect starts:
    setInterval every 1 second (if not paused):
        elapsed = elapsed + 1
        onTimeUpdate(elapsed) → parent component

User clicks Pause:
    ↓
    isPaused = true
    Timer stops

User clicks Resume:
    ↓
    isPaused = false
    Timer resumes

User clicks End Session:
    ↓
    isEnding = true
    Buttons disabled
    onEnd() callback triggered
```

## API Response Sequences

```
Timeline: Fund Locking Flow
──────────────────────────

t=0s    [Button click] "Lock Funds & Start"

t=100ms → sessionService.startSession()
         POST /sessions/start
         ├─ student_id: "user_1"
         ├─ listing_id: "session1"
         └─ reserve_amount: 45.00

t=150ms ← Backend locks funds
         Backend response:
         ├─ session_id: "sess_abc123"
         ├─ status: "active"
         ├─ reserve_amount: 45.00
         └─ transaction_id: "tx_xyz..."

t=200ms → milestonesService.createPaymentIntent()
         POST /milestones/intent
         ├─ amount: 45.00
         ├─ currency: "USD"
         ├─ description: "Payment for session"
         └─ metadata: {...}

t=250ms ← Backend creates intent
         Backend response:
         ├─ intent_id: "intent_xyz"
         ├─ escrow_id: "escrow_abc"
         ├─ status: "active"
         └─ total_amount: 45.00

t=300ms Component state updates:
        sessionData = {...}
        intentData = {...}
        Shows success alert

t=500ms Auto-navigate to ActiveSession
        location.pathname = "/active-session/sess_abc123"


Timeline: Session End Flow
──────────────────────────

t=0s    Session active, user watching video

t=5400s [Button click] "End Session"
        Payment time complete

t=5450ms → sessionService.endSession()
          POST /sessions/end
          ├─ session_id: "sess_abc123"
          ├─ completion_percentage: 95
          └─ engagement_metrics: {...}

t=5500ms ← Backend calculates and settles
          Backend response:
          ├─ session_id: "sess_abc123"
          ├─ duration_min: 90.0
          ├─ final_charge: 45.00
          ├─ refund_amount: 0.00
          └─ settle_tx_id: "tx_settle..."

t=5550ms → milestonesService.listMilestones()
          GET /milestones?session_id=sess_abc123

t=5600ms ← Backend returns milestones
          Response:
          ├─ milestones: [
          │  ├─ { id, description, status: "pending", ... }
          │  └─ { id, description, status: "pending", ... }
          │ ]
          └─ total: 2

t=5650ms → For each milestone:
          milestonesService.submitProof()
          POST /milestones/{id}/proof
          ├─ video_url: "https://..."
          └─ notes: "Completed 95%"

t=5700ms ← Backend completes milestones
          Response:
          ├─ milestone_id: "..."
          ├─ status: "completed"
          ├─ amount_released: 22.50
          └─ finternet_tx_id: "tx_..."

t=5750ms Component state updates:
        isEnding = false
        Shows completion message

t=6000ms Auto-navigate to Summary
        location.pathname = "/summary/sess_abc123"
```

## Error Scenario Flows

```
Scenario 1: Insufficient Balance
───────────────────────────────

[User clicks Lock Funds]
         ↓
[sessionService.startSession()]
         ↓
[Backend checks balance]
Balance < Reserve Amount
         ↓
Response 402 Unauthorized
{
  error: {
    message: "Insufficient balance",
    code: "INSUFFICIENT_BALANCE"
  }
}
         ↓
[Frontend catches error]
error = "Insufficient balance"
isLocking = false
         ↓
[Error alert displayed]
[User can click again to retry]


Scenario 2: Network Error
────────────────────────

[User clicks Lock Funds]
         ↓
[sessionService.startSession()]
         ↓
[Network timeout/failure]
         ↓
axios catches error
         ↓
[Frontend catches error]
error = "Network error" or "Failed to lock funds"
isLocking = false
         ↓
[Error alert displayed]
[User can click again to retry]


Scenario 3: Milestone Proof Failure (Non-critical)
──────────────────────────────────────────────────

[Session end successful]
         ↓
[Get milestone list]
         ↓
[Submit proof for milestone 1]
Success ✓
         ↓
[Submit proof for milestone 2]
Failure ✗
         ↓
[Frontend continues]
Log warning, don't stop execution
         ↓
[Navigate to summary anyway]
[User can manually complete milestones later]
```

## Component Hierarchy

```
App
├── AuthProvider
│   └── useAuth() available
└── Router
    ├── SessionDetail
    │   ├── WalletStatus
    │   └── [Alert components]
    │       ├── .alert-error
    │       ├── .alert-success
    │       └── .alert-info
    │
    ├── ActiveSession
    │   ├── ReactPlayer
    │   ├── SessionTimer
    │   │   ├── Timer display
    │   │   ├── Cost display
    │   │   └── Control buttons
    │   └── [Error banner]
    │
    └── Summary
        ├── Breakdown details
        └── Review form
```

---

This visual reference should help developers understand the complete flow and architecture of the API integration.
