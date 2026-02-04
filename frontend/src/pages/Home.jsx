import { useEffect, useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';
import { mockSessions, mockCategories } from '../lib/dataMocks';
import './Home.css';

export default function Home() {
  const [sessions, setSessions] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    let filtered = mockSessions;

    if (selectedCategory !== 'All') {
      filtered = filtered.filter((s) => s.category === selectedCategory);
    }

    if (searchQuery) {
      filtered = filtered.filter(
        (s) =>
          s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          s.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setSessions(filtered);
  }, [selectedCategory, searchQuery]);

  return (
    <div className="home-page">
      <h1>Welcome to Murph</h1>
      <p className="subtitle">
        Learn at your own pace. Pay only for what you use. Get reviewed by AI.
      </p>

      <div className="search-section">
        <div className="search-bar">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search courses..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="category-filter">
        <Filter size={20} />
        {mockCategories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`category-btn ${selectedCategory === cat ? 'active' : ''}`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="sessions-grid">
        {sessions.map((session) => (
          <Link key={session.id} to={`/session/${session.id}`}>
            <div className="session-card">
              <img src={session.thumbnail} alt={session.title} />
              <div className="session-info">
                <h3>{session.title}</h3>
                <p className="instructor">{session.instructor.name}</p>
                <div className="session-meta">
                  <span className="rating">⭐ {session.rating}</span>
                  <span className="duration">{session.duration} min</span>
                  <span className="price">${session.pricePerMinute}/min</span>
                </div>
                <div className="tags">
                  {session.tags.map((tag) => (
                    <span key={tag} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
