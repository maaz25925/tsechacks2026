import { useState, useRef, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Loader } from 'lucide-react';
import { askAI } from '../features/ai/aiService';
import './ChatSearch.css';

export default function ChatSearch() {
  const [params] = useSearchParams();
  const initialContext = params.get('context') || '';
  const navigate = useNavigate();
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize with context if provided
  useEffect(() => {
    if (initialContext && messages.length === 0) {
      setMessages([
        {
          role: 'user',
          content: initialContext,
          timestamp: new Date(),
        },
      ]);
      // Auto-fetch AI response for initial context
      fetchAIResponse(initialContext);
    }
  }, [initialContext]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const fetchAIResponse = async (query) => {
    setIsLoading(true);
    try {
      const response = await askAI(query);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.summary,
          suggestions: response.suggestions,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error('Chat AI error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: trimmed,
        timestamp: new Date(),
      },
    ]);
    setInput('');
    fetchAIResponse(trimmed);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-search-page">
      <div className="chat-header">
        <button className="back-btn" onClick={() => navigate(-1)} aria-label="Back">
          <ArrowLeft size={18} />
        </button>
        <div>
          <h2>AI Chat Search</h2>
          <p className="chat-subtitle">Ask anything about courses and learning paths</p>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <h3>👋 Welcome to AI Chat Search</h3>
            <p>Ask me anything about courses, topics, or learning paths. I'll help you find the best sessions!</p>
            <div className="sample-queries">
              <button onClick={() => setInput('What are the best React courses for beginners?')}>
                React for beginners
              </button>
              <button onClick={() => setInput('How do I learn backend development?')}>
                Backend development
              </button>
              <button onClick={() => setInput('Show me data science courses')}>
                Data science
              </button>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <p className="message-text">{msg.content}</p>
              {msg.suggestions && msg.suggestions.length > 0 && (
                <div className="message-suggestions">
                  <p className="suggestions-title">Related topics:</p>
                  <ul>
                    {msg.suggestions.map((sug, i) => (
                      <li key={i}>{sug}</li>
                    ))}
                  </ul>
                </div>
              )}
              <span className="message-time">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message message-assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <Loader size={16} className="spin" />
                <span>AI is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about courses, topics, or skills..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          aria-label="Send message"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
