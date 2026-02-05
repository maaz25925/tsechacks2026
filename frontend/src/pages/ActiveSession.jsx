import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import ReactPlayer from 'react-player';
import { discoveryService } from '../features/discovery/discoveryService';
import { mockSessions } from '../lib/dataMocks';
import SessionTimer from '../components/SessionTimer';
import './ActiveSession.css';

export default function ActiveSession() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [videoProgress, setVideoProgress] = useState(0);

  useEffect(() => {
    const fetchSession = async () => {
      setLoading(true);
      try {
        if (id?.startsWith('listing_')) {
          const data = await discoveryService.getListingDetail(id);
          setSession({
            id: id,
            title: data.title,
            instructor: {
              name: data.teacher_name || 'Instructor',
              avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=" + (data.teacher_name || "Instructor")
            },
            videoUrl: data.video_url, // Array or string
            duration: data.total_duration_min || 0,
          });
        } else {
          // Fallback to mocks
          const found = mockSessions.find((s) => s.id === id);
          setSession(found || null);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [id]);

  if (loading) return <div>Loading session...</div>;
  if (!session) {
    return <div>Session not found</div>;
  }

  const handleSessionEnd = () => {
    // Navigate to summary page
    navigate(`/summary/${session.id}`);
  };

  return (
    <div className="active-session">
      <div className="video-player-container">
        <ReactPlayer
          url={Array.isArray(session.videoUrl) ? session.videoUrl[0] : session.videoUrl}
          playing={true}
          controls={true}
          width="100%"
          height="100%"
          onProgress={(state) => setVideoProgress(state.played * 100)}
          onError={(e) => {
            console.error("Video playback error:", e);
            alert("Error playing video. The file might not exist or access is denied.");
          }}
        />
      </div>

      <SessionTimer session={session} onEnd={handleSessionEnd} />

      <div className="session-info">
        <h2>{session.title}</h2>
        <p>Instructor: {session.instructor.name}</p>
        <div className="progress-info">
          <p>Video Progress: {videoProgress.toFixed(0)}%</p>
        </div>
      </div>
    </div>
  );
}
