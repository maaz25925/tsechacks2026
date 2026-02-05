import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import ReactPlayer from 'react-player';
import { AlertCircle } from 'lucide-react';
import { mockSessions } from '../lib/dataMocks';
import sessionService from '../features/session/sessionService';
import milestonesService from '../features/session/milestonesService';
import SessionTimer from '../components/SessionTimer';
import './ActiveSession.css';

export default function ActiveSession() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [videoProgress, setVideoProgress] = useState(0);
  const [isEnding, setIsEnding] = useState(false);
  const [error, setError] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Try to use the actual session ID if it's a real one (starts with sess_),
  // otherwise use the mock session
  const isRealSession = id && id.startsWith('sess_');
  const mockSession = mockSessions.find((s) => s.id === id);
  const sessionId = isRealSession ? id : mockSession?.id;

  if (!isRealSession && !mockSession) {
    return <div>Session not found</div>;
  }

  const displaySession = mockSession || {
    id: sessionId,
    title: 'Session in Progress',
    videoUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    instructor: { name: 'Instructor' },
  };

  const handleSessionEnd = async () => {
    setIsEnding(true);
    setError(null);

    try {
      // If it's a real session (starts with sess_), end it properly via API
      if (isRealSession) {
        const completionPercentage = videoProgress; // Video progress as completion %
        const engagementMetrics = {
          videoProgress: videoProgress,
          elapsedTime: elapsedTime,
          timestamp: new Date().toISOString(),
        };

        const response = await sessionService.endSession({
          sessionId: id,
          completionPercentage,
          engagementMetrics,
        });

        console.log('Session ended successfully:', response);

        // If there are milestones, try to submit proof
        if (response.escrow_id) {
          try {
            // Get milestones for this session
            const milestonesResponse = await milestonesService.listMilestones({
              sessionId: id,
            });

            if (milestonesResponse.milestones && milestonesResponse.milestones.length > 0) {
              // Submit proof for each milestone
              for (const milestone of milestonesResponse.milestones) {
                if (milestone.status === 'pending') {
                  await milestonesService.submitProof(milestone.id, {
                    videoUrl: displaySession.videoUrl,
                    notes: `Completed ${completionPercentage.toFixed(0)}% of content`,
                  });
                  console.log(`Proof submitted for milestone ${milestone.id}`);
                }
              }
            }
          } catch (err) {
            console.warn('Could not submit milestone proofs:', err);
            // Continue anyway, this is not critical
          }
        }
      }

      // Navigate to summary page
      navigate(`/summary/${sessionId}`);
    } catch (err) {
      console.error('Error ending session:', err);
      setError(
        err.response?.data?.error?.message ||
        'Failed to end session. Please try again.'
      );
    } finally {
      setIsEnding(false);
    }
  };

  return (
    <div className="active-session">
      <div className="video-player-container">
        <ReactPlayer
          url={displaySession.videoUrl}
          playing={true}
          controls={true}
          width="100%"
          height="100%"
          onProgress={(state) => setVideoProgress(state.played * 100)}
        />
      </div>

      <SessionTimer
        session={displaySession}
        onEnd={handleSessionEnd}
        isEnding={isEnding}
        onTimeUpdate={setElapsedTime}
      />

      {error && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <p>{error}</p>
        </div>
      )}

      <div className="session-info">
        <h2>{displaySession.title}</h2>
        <p>Instructor: {displaySession.instructor.name}</p>
        <div className="progress-info">
          <p>Video Progress: {videoProgress.toFixed(0)}%</p>
        </div>
      </div>
    </div>
  );
}
