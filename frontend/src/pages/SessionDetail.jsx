import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Clock, User, Star, BookOpen, AlertCircle, CheckCircle } from 'lucide-react';
import { mockSessions } from '../lib/dataMocks';
import { useAuth } from '../features/auth/AuthProvider';
import sessionService from '../features/session/sessionService';
import WalletStatus from '../components/WalletStatus';
import './SessionDetail.css';

export default function SessionDetail() {
  const [entered, setEntered] = useState(false);
  const [isLocking, setIsLocking] = useState(false);
  const [error, setError] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [intentData, setIntentData] = useState(null);
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const session = mockSessions.find((s) => s.id === id);

  useEffect(() => {
    // animate hero image on mount
    const raf = requestAnimationFrame(() => setEntered(true));
    return () => cancelAnimationFrame(raf);
  }, []);

  if (!session) {
    return <div>Session not found</div>;
  }

  const estimatedCost = (session.duration * session.pricePerMinute).toFixed(2);

  const handleLockFunds = async () => {
    if (!user || user.role !== 'student') {
      setError('Please log in as a student to start a session');
      return;
    }

    setIsLocking(true);
    setError(null);

    try {
      // Calculate reserve amount (estimated cost)
      const reserveAmount = parseFloat(estimatedCost);

      // Start session - locks funds via Finternet
      const response = await sessionService.startSession({
        studentId: user.id,
        listingId: session.id,
        reserveAmount,
      });

      console.log('Session started successfully:', response);
      setSessionData(response);

      // Call Finternet API directly from frontend
      console.log('🔵 Calling Finternet API directly...');
      const finternetResponse = await fetch('https://api.fmm.finternetlab.io/api/v1/payment-intents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': 'sk_hackathon_7ac6f3dc218f73cb343d3be7296dac28',
        },
        body: JSON.stringify({
          amount: reserveAmount.toFixed(2),
          currency: 'USDC',
          type: 'DELIVERY_VS_PAYMENT',
          settlementMethod: 'OFF_RAMP_MOCK',
          settlementDestination: 'bank_account_murph',
          description: `Payment for ${session.title}`,
          metadata: {
            releaseType: 'MILESTONE_LOCKED',
            autoRelease: true,
            session_id: response.session_id,
            listing_id: session.id,
            student_id: user.id,
            teacher_id: session.instructor.id,
          },
        }),
      });

      const intentResponse = await finternetResponse.json();
      console.log('✅ Finternet API Response:', intentResponse);
      console.log('Payment URL:', intentResponse.data?.paymentUrl);
      setIntentData(intentResponse);

      // Redirect to Finternet payment URL (debit card input)
      const paymentUrl = intentResponse.data?.paymentUrl || intentResponse.paymentUrl;
      if (paymentUrl) {
        console.log('🚀 Opening Finternet payment page:', paymentUrl);
        // Store session data in sessionStorage for after payment
        sessionStorage.setItem('pendingSession', JSON.stringify({
          sessionId: response.session_id,
          intentId: intentResponse.id,
        }));
        // Open payment page in current window
        setTimeout(() => {
          window.location.href = paymentUrl;
        }, 1000);
      } else {
        console.warn('⚠️ No paymentUrl found in response');
        // Fallback: navigate to active session if no payment URL
        setTimeout(() => {
          navigate(`/active-session/${response.session_id}`);
        }, 1500);
      }
    } catch (err) {
      console.error('Error locking funds:', err);
      setError(
        err.response?.data?.error?.message ||
        'Failed to lock funds. Please try again.'
      );
    } finally {
      setIsLocking(false);
    }
  };

  const handleStartSession = () => {
    // Navigate to active session (should be called after fund lock)
    if (sessionData) {
      navigate(`/active-session/${sessionData.session_id}`);
    }
  };

  return (
    <div className="session-detail">
      <img
        src={session.thumbnail}
        alt={session.title}
        className={`hero-image ${entered ? 'entered' : ''}`}
      />

      <div className="content">
        <h1>{session.title}</h1>

        <div className="instructor-card">
          <img
            src={session.instructor.avatar}
            alt={session.instructor.name}
            className="instructor-avatar"
          />
          <div>
            <p className="instructor-label">Taught by</p>
            <p className="instructor-name">{session.instructor.name}</p>
          </div>
        </div>

        <div className="details">
          <div className="detail-item">
            <Clock size={20} />
            <div>
              <p className="label">Duration</p>
              <p className="value">{session.duration} minutes</p>
            </div>
          </div>
          <div className="detail-item">
            <Star size={20} />
            <div>
              <p className="label">Rating</p>
              <p className="value">
                {session.rating} ({session.reviews} reviews)
              </p>
            </div>
          </div>
          <div className="detail-item">
            <BookOpen size={20} />
            <div>
              <p className="label">Price per minute</p>
              <p className="value">${session.pricePerMinute}</p>
            </div>
          </div>
        </div>

        <div className="description">
          <h2>About this session</h2>
          <p>{session.description}</p>
        </div>

        <div className="learning-objectives">
          <h2>What you'll learn</h2>
          <ul>
            {session.learningObjectives.map((obj, idx) => (
              <li key={idx}>{obj}</li>
            ))}
          </ul>
        </div>

        <WalletStatus balance={2500} onConnect={() => {}} />

        {/* Error Alert */}
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            <p>{error}</p>
          </div>
        )}

        {/* Transaction Status */}
        {sessionData && (
          <div className="alert alert-success">
            <CheckCircle size={20} />
            <div>
              <p className="font-semibold">Funds Locked Successfully!</p>
              <p className="text-sm">Session ID: {sessionData.session_id}</p>
              <p className="text-sm">Transaction ID: {sessionData.transaction_id}</p>
              <p className="text-sm">Reserved Amount: ${sessionData.reserve_amount}</p>
            </div>
          </div>
        )}

        {/* Payment Intent Status */}
        {intentData && (
          <div className="alert alert-info">
            <CheckCircle size={20} />
            <div>
              <p className="font-semibold">Payment Intent Created</p>
              <p className="text-sm">Intent ID: {intentData.id}</p>
              <p className="text-sm">Status: {intentData.status}</p>
              <p className="text-sm">Amount: ${intentData.data?.amount || intentData.amount} {intentData.data?.currency || intentData.currency}</p>
              {(intentData.data?.paymentUrl || intentData.paymentUrl) && (
                <p className="text-sm" style={{ color: '#ff6b6b', marginTop: '8px' }}>
                  🔄 Redirecting to Finternet payment page in 1 second...
                </p>
              )}
            </div>
          </div>
        )}

        <div className="action-section">
          <div className="cost-estimate">
            <p className="estimate-label">Estimated Cost</p>
            <p className="estimate-value">${estimatedCost}</p>
            <p className="estimate-note">for {session.duration} minutes</p>
          </div>
          <button
            onClick={sessionData ? handleStartSession : handleLockFunds}
            className="start-btn"
            disabled={isLocking}
          >
            {isLocking
              ? 'Locking Funds...'
              : sessionData
                ? 'Start Session'
                : 'Lock Funds & Start'}
          </button>
        </div>
      </div>
    </div>
  );
}
