import { TrendingUp, Star } from 'lucide-react';
import { mockReviews } from '../lib/dataMocks';
import './TeacherDashboard.css';

export default function TeacherDashboard() {
  return (
    <div className="teacher-dashboard">
      <h1>Teacher Dashboard</h1>

      <div className="dashboard-grid">
        <div className="dash-card">
          <TrendingUp size={24} className="dash-icon" />
          <h3>Total Earnings</h3>
          <p className="value">$5,240.50</p>
          <p className="subtitle">This month</p>
        </div>
        <div className="dash-card">
          <Star size={24} className="dash-icon" />
          <h3>Average Rating</h3>
          <p className="value">4.8/5.0</p>
          <p className="subtitle">124 reviews</p>
        </div>
      </div>

      <div className="reviews-section">
        <h2>Recent Student Reviews</h2>
        <div className="reviews-list">
          {mockReviews.map((review) => (
            <div key={review.id} className="review-item">
              <div className="review-header">
                <div className="stars">
                  {'⭐'.repeat(review.rating)}
                </div>
                <span className="bonus">+${review.bonus} bonus</span>
              </div>
              <p className="review-text">{review.text}</p>
              <p className="review-meta">
                AI Score: {(review.aiValidation.score * 100).toFixed(0)}% · {review.createdAt.toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
