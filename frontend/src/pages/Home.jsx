import { useMemo, useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { mockSessions, mockCategories } from '../lib/dataMocks';
import './Home.css';

import { Search } from 'lucide-react';

const PLACEHOLDER_SVG = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='800'><rect width='100%' height='100%' fill='%23203134'/><text x='50%' y='50%' fill='%23ffffff' font-size='28' text-anchor='middle' dominant-baseline='middle'>No image</text></svg>`;

export default function Home({ selectedCategory = 'All', searchQuery = '', onCategoryChange }) {
  const [activeCategory, setActiveCategory] = useState(selectedCategory);
  const navigate = useNavigate();

  useEffect(() => {
    setActiveCategory(selectedCategory);
  }, [selectedCategory]);

  useEffect(() => {
    // listen for Enter on .search-input and navigate to /search
    const handler = (e) => {
      if (e.key === 'Enter') {
        const active = document.activeElement;
        if (active && active.classList && active.classList.contains('search-input')) {
          const v = (active.value || '').trim();
          if (v) navigate(`/search?q=${encodeURIComponent(v)}`);
        }
      }
    };

    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [navigate]);

  useEffect(() => {
    const onAppSearch = (e) => {
      const q = (e?.detail || '').toString().trim();
      if (q) navigate(`/search?q=${encodeURIComponent(q)}`);
    };
    window.addEventListener('app:search', onAppSearch);
    return () => window.removeEventListener('app:search', onAppSearch);
  }, [navigate]);

  const handleCategoryClick = (cat) => {
    setActiveCategory(cat);
    if (onCategoryChange) onCategoryChange(cat);
  };
  const sessions = useMemo(() => {
    let filtered = [...mockSessions];

    // DEV: Override first card with real listing ID for testing
    if (filtered.length > 0) {
      filtered[0] = {
        ...filtered[0],
        id: "listing_2e51bac18dc64cbeb3399c7b049a1e93"
      };
    }

    if (activeCategory && activeCategory !== 'All') {
      filtered = filtered.filter((s) => s.category === activeCategory);
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (s) =>
          s.title.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q)
      );
    }

    return filtered;
  }, [activeCategory, searchQuery]);

  return (
    <div className="home-page">
      <div className="category-bar" role="tablist" aria-label="Categories">
        {mockCategories.map((cat) => (
          <button
            key={cat}
            className={`category-chip ${activeCategory === cat ? 'active' : ''}`}
            onClick={() => handleCategoryClick(cat)}
            role="tab"
            aria-selected={activeCategory === cat}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Small search icon: navigate to search page */}
      {/* <button
        className="home-search-btn"
        aria-label="Open search"
        onClick={() => {
          const inp = document.querySelector('.search-input');
          if (inp) {
            const v = (inp.value || '').trim();
            if (v) navigate(`/search?q=${encodeURIComponent(v)}`);
            else inp.focus();
          } else {
            navigate('/search');
          }
        }}
      >
        <Search size={18} />
      </button> */}
      <div className="sessions-grid">
        {sessions.map((session) => (
          <Link key={session.id} to={`/session/${session.id}`} className="session-link">
            <div className="session-card">
              <div className="card-thumbnail-wrapper">
                <img
                  src={session.thumbnail}
                  alt={session.title}
                  className="card-thumbnail"
                  onError={(e) => {
                    e.currentTarget.onerror = null;
                    e.currentTarget.src = PLACEHOLDER_SVG;
                  }}
                />
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
