import React, { useState } from 'react';
import Sidebar from './Sidebar.jsx';
import TopBar from './TopBar.jsx';
import './Layout.css';

function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className={`app-layout ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      <Sidebar isOpen={sidebarOpen} onToggleSidebar={toggleSidebar} />
      <TopBar 
        onSearchChange={setSearchQuery}
        onCategoryChange={setSelectedCategory}
        selectedCategory={selectedCategory}
        searchQuery={searchQuery}
        sidebarOpen={sidebarOpen}
      />
      <main className="main-content" style={{ marginLeft: sidebarOpen ? '256px' : '0' }}>
        {React.cloneElement(children, {
          selectedCategory,
          searchQuery,
          onSearchChange: setSearchQuery,
          onCategoryChange: setSelectedCategory
        })}
      </main>
    </div>
  );
}

export default Layout;
