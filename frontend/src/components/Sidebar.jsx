import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, Search, Grid, User, LogOut, Upload } from 'lucide-react';
import { useAuth } from '../features/auth/AuthProvider.jsx';
import './Sidebar.css';

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const menuItems = [
    { path: '/home', icon: Home, label: 'Home' },
    { path: '/discover', icon: Search, label: 'Discover' },
    { path: '/dashboard', icon: Grid, label: 'Dashboard' },
    { path: '/wallet', icon: User, label: 'Wallet' },
    { path: '/upload', icon: Upload, label: 'Upload' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="logo text-center">Murph</h1>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <button className="logout-btn" onClick={handleLogout}>
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}
