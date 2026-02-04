import React from 'react';
import { Moon, Sun, Search } from 'lucide-react';
import { useTheme } from '../features/theme/ThemeProvider.jsx';
import { mockCategories } from '../lib/dataMocks';
import './TopBar.css';

export default function TopBar({ onSearchChange, onCategoryChange, selectedCategory, searchQuery }) {
  const { isDarkMode, toggleTheme } = useTheme();
  const inputRef = React.useRef(null);

  const handleIconClick = () => {
    const v = (inputRef.current?.value || '').trim();
    if (v) {
      window.dispatchEvent(new CustomEvent('app:search', { detail: v }));
    } else {
      inputRef.current?.focus();
    }
  };

  return (
    <div className="top-bar">
      <div className="navbar-top">
        <div className="search-section">
          <div className="search-bar">
            <input
              ref={inputRef}
              type="text"
              className="search-input"
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
            />
            <button className="search-btn" onClick={handleIconClick} aria-label="Search">
              <Search size={18} />
            </button>
          </div>
        </div>

        <button 
          className="theme-toggle-btn" 
          onClick={toggleTheme} 
          title={isDarkMode ? 'Light Mode' : 'Dark Mode'}
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>

      {/* Category filter moved to Home page for a single, consistent bar */}
    </div>
  );
}
