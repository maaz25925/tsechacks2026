import AIChat from '../components/AIChat';
import './Discover.css';

export default function Discover() {
  return (
    <div className="discover-page">
      <h1>Discover with AI</h1>
      <p className="subtitle">
        Tell our AI what you want to learn, and get personalized recommendations.
      </p>

      <div className="chat-container">
        <AIChat />
      </div>
    </div>
  );
}
