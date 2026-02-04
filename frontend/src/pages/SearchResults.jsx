import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { mockSessions } from '../lib/dataMocks';
import { askAI } from '../features/ai/aiService';
import './Home.css';
import '../components/SearchOverlay.css';
import './SearchResults.css';
import { ArrowLeft, MessageSquare, Loader } from 'lucide-react';

export default function SearchResults() {
  const [params] = useSearchParams();
  const q = (params.get('q') || '').trim();
  const navigate = useNavigate();
  const [aiResponse, setAiResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const sessions = mockSessions.filter((s) => {
    if (!q) return true;
    const lc = q.toLowerCase();
    return s.title.toLowerCase().includes(lc) || s.description.toLowerCase().includes(lc);
  });

  useEffect(() => {
    if (!q) return;
    setIsLoading(true);
    askAI(q)
      .then((response) => {
        setAiResponse(response);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error('AI request failed', err);
        setAiResponse({ summary: 'Sorry, I couldn\'t process your request. Please try again.' });
        setIsLoading(false);
      });
  }, [q]);

  return (
    <div className="search-page">
      <div className="search-page-header">
        <button className="back-btn" onClick={() => navigate(-1)} aria-label="Back">
          <ArrowLeft size={18} />
        </button>
        <h2>Search results for "{q}"</h2>
      </div>

      {/* AI Response Section */}
      <div className="ai-response-section">
        {isLoading ? (
          <div className="ai-loading">
            <Loader size={20} className="spin" />
            <span>AI is analyzing your query...</span>
          </div>
        ) : aiResponse ? (
          <>
            <div className="ai-response-content">
              <h3 className="ai-label">AI Summary</h3>
              <p className="ai-text">{aiResponse.summary}</p>
              {aiResponse.suggestions && aiResponse.suggestions.length > 0 && (
                <div className="ai-suggestions">
                  <p className="suggestions-label">You might also want to explore:</p>
                  <ul>
                    {aiResponse.suggestions.map((sug, i) => (
                      <li key={i}>{sug}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <button
              className="chat-btn"
              onClick={() => navigate(`/chat?context=${encodeURIComponent(q)}`)}
            >
              <MessageSquare size={18} />
              Continue in Chat
            </button>
          </>
        ) : null}
      </div>

      <div className="related-label">Related Sessions</div>
      <div className="search-results-grid">
        {sessions.length === 0 ? (
          <div className="no-results">No results — try a different query</div>
        ) : (
          sessions.map((s) => (
            <Link key={s.id} to={`/session/${s.id}`} className="result-card modern">
              <div className="card-thumbnail-wrapper">
                <img src={s.thumbnail} alt={s.title} className="card-thumbnail" />
                <div className="card-overlay"><span className="duration-hex">{s.duration}</span></div>
              </div>
              <div className="session-info">
                <h3 className="session-title">{s.title}</h3>
                <p className="instructor-name">{s.instructor.name}</p>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
