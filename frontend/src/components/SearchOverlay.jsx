import React from 'react';
import { X } from 'lucide-react';
import './SearchOverlay.css';

export default function SearchOverlay({ query, sessions = [], onClose }) {
  return (
    <div className="search-overlay" role="dialog" aria-modal="true">
      <div className="search-overlay-backdrop" onClick={onClose} />

      <div className="search-overlay-panel">
        <header className="search-overlay-header">
          <div>
            <h2 className="query-title">Search results for "{query}"</h2>
            <p className="query-sub">AI-powered suggestions & related sessions</p>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close search results">
            <X size={20} />
          </button>
        </header>

        <section className="search-results-grid">
          {sessions.length === 0 ? (
            <div className="no-results">No results — try a different query</div>
          ) : (
            sessions.map((s) => (
              <article key={s.id} className="result-card modern">
                <div className="card-thumbnail-wrapper">
                  <img src={s.thumbnail} alt={s.title} className="card-thumbnail" />
                  <div className="menu-dots">⋮</div>
                  <div className="visualizer"><div className="ring" /><span className="center-timer">{s.duration}:00</span></div>
                  <div className="card-overlay"><span className="duration-hex">{s.duration}</span></div>
                </div>

                <div className="session-info">
                  <h3 className="session-title">{s.title}</h3>
                  <p className="instructor-name">{s.instructor.name}</p>
                </div>
              </article>
            ))
          )}
        </section>
      </div>
    </div>
  );
}
