import { Link, useLocation } from 'react-router-dom';
import { Home, Search, Grid, User, LogOut, Upload, Menu, X } from 'lucide-react';
import { useState } from 'react';
import './Sidebar.css';

export default function Sidebar() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  const menuItems = [
    { path: '/home', icon: Home, label: 'Home' },
    { path: '/discover', icon: Search, label: 'Discover' },
    { path: '/dashboard', icon: Grid, label: 'Dashboard' },
    { path: '/wallet', icon: User, label: 'Wallet' },
    { path: '/upload', icon: Upload, label: 'Upload' },
  ];

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const closeSidebar = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* Hamburger/Close Button - Only visible on mobile */}
      <button className="hamburger-btn" onClick={toggleSidebar} aria-label="Toggle menu">
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay - Only visible on mobile when sidebar is open */}
      {isOpen && <div className="sidebar-overlay" onClick={closeSidebar}></div>}

      {/* Sidebar */}
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
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
                onClick={closeSidebar}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <button className="logout-btn">
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
}
