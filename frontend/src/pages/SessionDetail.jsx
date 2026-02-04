import { useParams, useNavigate } from 'react-router-dom';
import { Clock, User, Star, BookOpen } from 'lucide-react';
import { mockSessions } from '../lib/dataMocks';
import WalletStatus from '../components/WalletStatus';
import './SessionDetail.css';

export default function SessionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const session = mockSessions.find((s) => s.id === id);

  if (!session) {
    return <div>Session not found</div>;
  }

  const estimatedCost = (session.duration * session.pricePerMinute).toFixed(2);

  return (
    <div className="session-detail">
      <img src={session.thumbnail} alt={session.title} className="hero-image" />

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

        <div className="action-section">
          <div className="cost-estimate">
            <p className="estimate-label">Estimated Cost</p>
            <p className="estimate-value">${estimatedCost}</p>
            <p className="estimate-note">for {session.duration} minutes</p>
          </div>
          <button
            onClick={() => navigate(`/active-session/${session.id}`)}
            className="start-btn"
          >
            Start Session
          </button>
        </div>
      </div>
    </div>
  );
}
