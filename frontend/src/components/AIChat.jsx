import { useState } from 'react';
import { Send } from 'lucide-react';
import { aiService } from '../features/ai/aiService';
import './AIChat.css';

export default function AIChat() {
  const [messages, setMessages] = useState([
    {
      id: 'msg0',
      type: 'ai',
      text: 'Hi! I am Murph AI. Tell me what you want to learn, and I will recommend the perfect course for you.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: 'msg_' + Date.now(),
      type: 'user',
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await aiService.discoverCourse(input);
      const aiMessage = {
        id: 'msg_' + Date.now(),
        type: 'ai',
        text: response.message,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('AI request failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-chat">
      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.type}`}>
            <div className="message-content">{msg.text}</div>
          </div>
        ))}
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Describe what you want to learn..."
          disabled={loading}
          className="chat-input"
        />
        <button onClick={handleSend} disabled={loading} className="send-btn">
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
