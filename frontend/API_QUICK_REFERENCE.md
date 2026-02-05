# Frontend API Integration - Quick Reference

## Quick Start Examples

### Example 1: Start a Session

```javascript
import sessionService from '../features/session/sessionService';
import milestonesService from '../features/session/milestonesService';

// In your component
const handleStartSession = async () => {
  try {
    // Start session and lock funds
    const sessionResponse = await sessionService.startSession({
      studentId: 'user_123',
      listingId: 'session1',
      reserveAmount: 45.00
    });

    console.log('Session started:', sessionResponse);
    // Response: { session_id, status, reserve_amount, transaction_id }

    // Create payment intent for milestones
    const intentResponse = await milestonesService.createPaymentIntent({
      amount: 45.00,
      currency: 'USD',
      description: `Payment for session`,
      metadata: {
        session_id: sessionResponse.session_id,
        student_id: 'user_123'
      }
    });

    console.log('Payment intent created:', intentResponse);
    // Response: { intent_id, escrow_id, status, total_amount }

    // Navigate to active session
    navigate(`/active-session/${sessionResponse.session_id}`);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
};
```

### Example 2: End a Session and Submit Proof

```javascript
import sessionService from '../features/session/sessionService';
import milestonesService from '../features/session/milestonesService';

const handleEndSession = async (sessionId, videoProgress) => {
  try {
    // End session
    const endResponse = await sessionService.endSession({
      sessionId: sessionId,
      completionPercentage: videoProgress,
      engagementMetrics: {
        videoProgress: videoProgress,
        timeSpent: 5400 // seconds
      }
    });

    console.log('Session ended:', endResponse);

    // Get milestones for this session
    const milestonesResponse = await milestonesService.listMilestones({
      sessionId: sessionId
    });

    // Submit proof for each pending milestone
    for (const milestone of milestonesResponse.milestones) {
      if (milestone.status === 'pending') {
        const proofResponse = await milestonesService.submitProof(
          milestone.id,
          {
            videoUrl: 'https://example.com/video',
            notes: `Completed ${videoProgress.toFixed(0)}% of content`
          }
        );
        console.log('Proof submitted:', proofResponse);
      }
    }
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
};
```

### Example 3: Get Session Details and Payments

```javascript
const getSessionInfo = async (sessionId) => {
  try {
    // Get session details
    const session = await sessionService.getSession(sessionId);
    console.log('Session:', session);

    // Get payment records
    const payments = await sessionService.getSessionPayments(sessionId);
    console.log('Payments:', payments);

    // Get escrow details
    const escrow = await milestonesService.getEscrow(payments.intent_id);
    console.log('Escrow:', escrow);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
};
```

### Example 4: Create Multiple Milestones

```javascript
const createMilestones = async (escrowId, sessionId) => {
  const milestones = [
    {
      index: 0,
      description: 'Phase 1 - Introduction',
      amount: 10,
      percentage: 25
    },
    {
      index: 1,
      description: 'Phase 2 - Core Content',
      amount: 15,
      percentage: 50
    },
    {
      index: 2,
      description: 'Phase 3 - Advanced Topics',
      amount: 10,
      percentage: 25
    }
  ];

  try {
    for (const milestone of milestones) {
      const response = await milestonesService.createMilestone({
        escrowId: escrowId,
        sessionId: sessionId,
        ...milestone
      });
      console.log(`Milestone ${milestone.index} created:`, response);
    }
  } catch (error) {
    console.error('Error creating milestones:', error.response?.data);
  }
};
```

## Error Handling Patterns

### Pattern 1: Graceful Error Display

```javascript
const [error, setError] = useState(null);
const [isLoading, setIsLoading] = useState(false);

const handleAction = async () => {
  setIsLoading(true);
  setError(null);

  try {
    const response = await sessionService.startSession({ /* ... */ });
    // Handle success
  } catch (err) {
    setError(
      err.response?.data?.error?.message || 'An error occurred'
    );
  } finally {
    setIsLoading(false);
  }
};
```

### Pattern 2: Retry Logic

```javascript
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      // Exponential backoff: 1s, 2s, 4s
      await new Promise(resolve => 
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    }
  }
};

// Usage
const sessionData = await retryWithBackoff(
  () => sessionService.startSession({ /* ... */ })
);
```

### Pattern 3: Sequential API Calls

```javascript
const startSessionWithIntentAndMilestones = async ({ 
  studentId, 
  listingId, 
  reserveAmount 
}) => {
  try {
    // Step 1: Start session
    const sessionResponse = await sessionService.startSession({
      studentId,
      listingId,
      reserveAmount
    });

    // Step 2: Create payment intent
    const intentResponse = await milestonesService.createPaymentIntent({
      amount: reserveAmount,
      currency: 'USD',
      description: `Payment for listing ${listingId}`,
      metadata: { session_id: sessionResponse.session_id }
    });

    // Step 3: Create milestones (if needed)
    const milestones = await Promise.all([
      milestonesService.createMilestone({
        escrowId: intentResponse.escrow_id,
        sessionId: sessionResponse.session_id,
        index: 0,
        description: 'Complete content',
        amount: reserveAmount,
        percentage: 100
      })
    ]);

    return {
      session: sessionResponse,
      intent: intentResponse,
      milestones: milestones
    };
  } catch (error) {
    console.error('Pipeline failed:', error);
    throw error;
  }
};
```

## Integration Points

### In SessionDetail.jsx

```jsx
import { useAuth } from '../features/auth/AuthProvider';
import sessionService from '../features/session/sessionService';
import milestonesService from '../features/session/milestonesService';

export function SessionDetail() {
  const { user } = useAuth();
  
  const handleLockFunds = async () => {
    const session = await sessionService.startSession({
      studentId: user.id,
      listingId: sessionId,
      reserveAmount: estimatedCost
    });
    
    const intent = await milestonesService.createPaymentIntent({
      amount: estimatedCost,
      currency: 'USD',
      description: 'Session payment'
    });
    
    navigate(`/active-session/${session.session_id}`);
  };
}
```

### In ActiveSession.jsx

```jsx
import sessionService from '../features/session/sessionService';

export function ActiveSession() {
  const handleSessionEnd = async () => {
    const breakdown = await sessionService.endSession({
      sessionId: id,
      completionPercentage: videoProgress,
      engagementMetrics: { videoProgress }
    });
    
    navigate(`/summary/${id}`);
  };
}
```

## Response Structures

### SessionStartResponse
```javascript
{
  session_id: "sess_a1b2c3d4e5f6",
  status: "active",
  reserve_amount: 45.00,
  transaction_id: "tx_abc123def456"
}
```

### SessionEndBreakdown
```javascript
{
  session_id: "sess_a1b2c3d4e5f6",
  listing_id: "session1",
  teacher_id: "user_2",
  student_id: "user_1",
  start_time: "2024-02-05T10:30:00Z",
  end_time: "2024-02-05T11:45:00Z",
  duration_min: 75.5,
  completion_percentage: 95,
  reserve_amount: 45.00,
  final_amount_charged: 37.50,
  refund_amount: 7.50,
  settle_transaction_id: "tx_settle123"
}
```

### PaymentIntentResponse
```javascript
{
  intent_id: "intent_xyz789",
  escrow_id: "escrow_abc123",
  status: "active",
  total_amount: 45.00
}
```

### MilestoneResponse
```javascript
{
  id: "milestone_123",
  escrow_id: "escrow_abc123",
  session_id: "sess_a1b2c3d4e5f6",
  index: 0,
  description: "Phase 1",
  amount: 22.50,
  percentage: 50,
  status: "pending",
  proof_data: null,
  created_at: "2024-02-05T10:30:00Z"
}
```

## Common Patterns

### Loading States
```javascript
const [isLoading, setIsLoading] = useState(false);

return (
  <button onClick={handleAction} disabled={isLoading}>
    {isLoading ? 'Processing...' : 'Action'}
  </button>
);
```

### Error Alerts
```javascript
{error && (
  <div className="alert alert-error">
    <AlertIcon />
    <p>{error}</p>
  </div>
)}
```

### Success Confirmation
```javascript
{sessionData && (
  <div className="alert alert-success">
    <CheckIcon />
    <div>
      <p>Session started successfully!</p>
      <p>Session ID: {sessionData.session_id}</p>
    </div>
  </div>
)}
```

## Testing Checklist

- [ ] Session starts and funds lock
- [ ] Payment intent created
- [ ] Navigation to active session works
- [ ] Timer increments correctly
- [ ] Video progress tracked
- [ ] Session ends and charges calculated
- [ ] Milestones submitted with proof
- [ ] Error messages display
- [ ] Retry logic works
- [ ] Auth token included in all requests

## Configuration

Set backend URL in `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
```

For production:
```
VITE_API_BASE_URL=https://api.production.com
```

## Support

For issues or questions:
1. Check browser console for detailed error logs
2. Review [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for architecture details
3. Check backend logs for API errors
4. Review curl command examples in the guide
