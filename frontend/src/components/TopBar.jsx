import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../features/theme/ThemeProvider.jsx';
import './TopBar.css';

export default function TopBar() {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <div className="top-bar">
      <button 
        className="theme-toggle-btn" 
        onClick={toggleTheme} 
        title={isDarkMode ? 'Light Mode' : 'Dark Mode'}
      >
        {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
      </button>
    </div>
  );
}
