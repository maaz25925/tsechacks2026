import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { mockSessions } from '../lib/dataMocks';
import ReviewForm from '../components/ReviewForm';
import './Summary.css';

export default function Summary() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const session = mockSessions.find((s) => s.id === sessionId);
  const [review, setReview] = useState(null);

  // Mock session data
  const sessionDuration = 45;
  const elapsedMinutes = 45;
  const totalCost = (elapsedMinutes * (session?.pricePerMinute || 0.5)).toFixed(2);
  const reviewBonus = review?.bonus || 0;

  if (!session) {
    return <div>Session not found</div>;
  }

  const handleReviewSubmit = (reviewData) => {
    setReview(reviewData);
  };

  return (
    <div className="summary-page">
      <div className="summary-header">
        <h1>Session Complete! 🎉</h1>
        <p>Thank you for learning with us</p>
      </div>

      <div className="summary-grid">
        <div className="summary-card">
          <h3>Session Duration</h3>
          <p className="value">{elapsedMinutes} minutes</p>
        </div>
        <div className="summary-card">
          <h3>Cost</h3>
          <p className="value">${totalCost}</p>
        </div>
        <div className="summary-card">
          <h3>Instructor</h3>
          <p className="value">{session.instructor.name}</p>
        </div>
        {review && (
          <div className="summary-card success">
            <h3>Bonus Earned</h3>
            <p className="value green">${reviewBonus}</p>
          </div>
        )}
      </div>

      {!review ? (
        <div className="review-section">
          <h2>Share Your Feedback</h2>
          <ReviewForm sessionId={sessionId} onSubmit={handleReviewSubmit} />
        </div>
      ) : (
        <div className="review-success">
          <div className="success-icon">✓</div>
          <h2>Thank you for your review!</h2>
          <p>
            Your feedback helps us improve and you earned{' '}
            <strong>${reviewBonus}</strong> bonus credits!
          </p>
          <p>
            Review Score: <strong>{(review.aiValidation.score * 100).toFixed(0)}%</strong>
          </p>
        </div>
      )}

      <button onClick={() => navigate('/')} className="back-home-btn">
        Back to Home
      </button>
    </div>
  );
}
