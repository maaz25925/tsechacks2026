import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Clock, User, Star, BookOpen } from 'lucide-react';
import { mockSessions } from '../lib/dataMocks';
import { discoveryService } from '../features/discovery/discoveryService';
import WalletStatus from '../components/WalletStatus';
import './SessionDetail.css';

const PLACEHOLDER_AVATAR = "https://api.dicebear.com/7.x/avataaars/svg?seed=Instructor";

export default function SessionDetail() {
  const [entered, setEntered] = useState(false);
  const { id } = useParams();
  const navigate = useNavigate();

  // Try to find in mocks first
  const mockSession = mockSessions.find((s) => s.id === id);
  const [session, setSession] = useState(mockSession || null);
  const [loading, setLoading] = useState(id?.startsWith('listing_')); // Only load if it's a real ID
  const [error, setError] = useState(null);

  useEffect(() => {
    // animate hero image on mount
    const raf = requestAnimationFrame(() => setEntered(true));
    return () => cancelAnimationFrame(raf);
  }, []);

  useEffect(() => {
    // If it's a real listing ID, fetch from API
    if (id?.startsWith('listing_')) {
      const fetchSession = async () => {
        try {
          setLoading(true);
          const data = await discoveryService.getListingDetail(id);

          setSession({
            id: id,
            title: data.title,
            description: data.description,
            thumbnail: data.thumbnail,
            instructor: {
              name: data.teacher_name || 'Instructor',
              avatar: PLACEHOLDER_AVATAR
            },
            duration: data.total_duration_min,
            rating: data.reviews_rating || 'New',
            reviews: 0,
            pricePerMinute: data.price_per_min,
            learningObjectives: data.course_outcomes || [],
            videoUrl: data.video_url,
            transcription: data.transcription
          });
        } catch (err) {
          console.error('Failed to fetch session details:', err);
          setError('Failed to load session details');
        } finally {
          setLoading(false);
        }
      };

      fetchSession();
    }
  }, [id]);

  if (loading) return <div className="session-detail-loading">Loading details...</div>;
  if (error) return <div className="session-detail-error">{error}</div>;
  if (!session) return <div className="session-detail-not-found">Session not found</div>;

  const estimatedCost = (session.duration * session.pricePerMinute).toFixed(2);
  const videoSrc = session.videoUrl
    ? (Array.isArray(session.videoUrl) ? session.videoUrl[0] : session.videoUrl)
    : null;

  return (
    <div className="session-detail">
      {videoSrc ? (
        <video
          src={videoSrc}
          className={`hero-video ${entered ? 'entered' : ''}`}
          controls
          poster={session.thumbnail}
          playsInline
        />
      ) : (
        <img
          src={session.thumbnail}
          alt={session.title}
          className={`hero-image ${entered ? 'entered' : ''}`}
        />
      )}

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

        <WalletStatus balance={2500} onConnect={() => { }} />

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
