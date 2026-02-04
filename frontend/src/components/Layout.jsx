import React from 'react';
import Sidebar from './Sidebar.jsx';
import TopBar from './TopBar.jsx';
import './Layout.css';

function Layout({ children }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <TopBar />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

export default Layout;
