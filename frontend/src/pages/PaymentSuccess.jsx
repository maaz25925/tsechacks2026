import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export function PaymentSuccess() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const intent = searchParams.get('intent');
    console.log('Payment successful! Intent:', intent);

    // Get pending session from sessionStorage
    const pendingSession = sessionStorage.getItem('pendingSession');
    if (pendingSession) {
      const sessionData = JSON.parse(pendingSession);
      console.log('Navigating to active session:', sessionData.sessionId);
      
      // Clear the pending session
      sessionStorage.removeItem('pendingSession');
      
      // Redirect to active session after a short delay
      setTimeout(() => {
        navigate(`/session/${sessionData.sessionId}`, { replace: true });
      }, 1500);
    } else {
      // Fallback: navigate to discover page
      setTimeout(() => {
        navigate('/discover', { replace: true });
      }, 2000);
    }
  }, [navigate, searchParams]);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      textAlign: 'center',
    }}>
      <div>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>✅ Payment Successful!</h1>
        <p style={{ fontSize: '1.1rem', marginBottom: '2rem' }}>
          Your session is being activated...
        </p>
        <div style={{
          width: '50px',
          height: '50px',
          border: '5px solid rgba(255,255,255,0.3)',
          borderTop: '5px solid white',
          borderRadius: '50%',
          margin: '0 auto',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p style={{ marginTop: '2rem', opacity: 0.8 }}>
          Redirecting to your session...
        </p>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
}

export default PaymentSuccess;
