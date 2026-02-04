import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import ReactPlayer from 'react-player';
import { mockSessions } from '../lib/dataMocks';
import SessionTimer from '../components/SessionTimer';
import './ActiveSession.css';

export default function ActiveSession() {
  const { id } = useParams();
  const navigate = useNavigate();
  const session = mockSessions.find((s) => s.id === id);
  const [videoProgress, setVideoProgress] = useState(0);

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
          url={session.videoUrl}
          playing={true}
          controls={true}
          width="100%"
          height="100%"
          onProgress={(state) => setVideoProgress(state.played * 100)}
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
