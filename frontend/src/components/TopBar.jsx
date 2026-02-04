import { Moon, Sun, Search, Filter } from 'lucide-react';
import { useTheme } from '../features/theme/ThemeProvider.jsx';
import { mockCategories } from '../lib/dataMocks';
import './TopBar.css';

export default function TopBar({ onSearchChange, onCategoryChange, selectedCategory, searchQuery }) {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <div className="top-bar">
      <div className="navbar-top">
        <div className="search-section">
          <div className="search-bar">
            <Search size={20} />
            <input
              type="text"
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
            />
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

      <div className="category-filter">
        <Filter size={20} />
        {mockCategories.map((cat) => (
          <button
            key={cat}
            onClick={() => onCategoryChange(cat)}
            className={`category-btn ${selectedCategory === cat ? 'active' : ''}`}
          >
            {cat}
          </button>
        ))}
      </div>
    </div>
  );
}
