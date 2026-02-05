import { useEffect, useState } from 'react';
import { Clock, DollarSign } from 'lucide-react';
import './SessionTimer.css';

export default function SessionTimer({ session, onEnd, isEnding = false, onTimeUpdate }) {
  const [elapsed, setElapsed] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const estimatedCost = (elapsed / 60) * session.pricePerMinute;

  useEffect(() => {
    if (isPaused) return;

    const timer = setInterval(() => {
      setElapsed((prev) => {
        const newElapsed = prev + 1;
        // Notify parent component of time update
        if (onTimeUpdate) {
          onTimeUpdate(newElapsed);
        }
        return newElapsed;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isPaused, onTimeUpdate]);

  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;

  const formatTime = (m, s) => {
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  const handleEndSession = async () => {
    if (onEnd) {
      await onEnd();
    }
  };

  return (
    <div className="session-timer">
      <div className="timer-display">
        <Clock size={32} className="timer-icon" />
        <div className="timer-info">
          <div className="timer-value">{formatTime(minutes, seconds)}</div>
          <div className="timer-label">Elapsed</div>
        </div>
      </div>

      <div className="cost-display">
        <DollarSign size={32} className="cost-icon" />
        <div className="cost-info">
          <div className="cost-value">${estimatedCost.toFixed(2)}</div>
          <div className="cost-label">Est. Cost</div>
        </div>
      </div>

      <div className="timer-controls">
        <button
          onClick={() => setIsPaused(!isPaused)}
          className="pause-btn"
          disabled={isEnding}
        >
          {isPaused ? 'Resume' : 'Pause'}
        </button>
        <button
          onClick={handleEndSession}
          className="end-btn"
          disabled={isEnding}
        >
          {isEnding ? 'Ending...' : 'End Session'}
        </button>
      </div>
    </div>
  );
}
