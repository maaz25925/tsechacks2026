import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { mockSessions, mockCategories } from '../lib/dataMocks';
import './Home.css';

export default function Home({ selectedCategory = 'All', searchQuery = '', onSearchChange, onCategoryChange }) {
  const [sessions, setSessions] = useState([]);

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
      <div className="sessions-grid">
        {sessions.map((session) => (
          <Link key={session.id} to={`/session/${session.id}`} className="session-link">
            <div className="session-card">
              <div className="card-thumbnail-wrapper">
                <img src={session.thumbnail} alt={session.title} className="card-thumbnail" />
                <div className="card-overlay">
                  <span className="duration-badge">{session.duration} min</span>
                </div>
              </div>
              <div className="session-info">
                <h3 className="session-title">{session.title}</h3>
                <p className="instructor-name">{session.instructor.name}</p>
                <div className="session-stats">
                  <div className="rating-section">
                    <span className="rating">⭐ {session.rating}</span>
                  </div>
                  <div className="price-section">
                    <span className="price">${session.pricePerMinute}/min</span>
                  </div>
                </div>
                <div className="tags-section">
                  {session.tags.map((tag) => (
                    <span key={tag} className="tag-badge">
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
