import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Home from './pages/Home.jsx';
import Discover from './pages/Discover.jsx';
import SessionDetail from './pages/SessionDetail.jsx';
import ActiveSession from './pages/ActiveSession.jsx';
import Summary from './pages/Summary.jsx';
import Wallet from './pages/Wallet.jsx';
import TeacherDashboard from './pages/TeacherDashboard.jsx';
import CreatorUpload from './pages/CreatorUpload.jsx';
import './App.css';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-white dark:bg-slate-950">
        <Sidebar />
        <main className="flex-1 ml-64 p-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/discover" element={<Discover />} />
            <Route path="/session/:id" element={<SessionDetail />} />
            <Route path="/active-session/:id" element={<ActiveSession />} />
            <Route path="/summary/:sessionId" element={<Summary />} />
            <Route path="/wallet" element={<Wallet />} />
            <Route path="/dashboard" element={<TeacherDashboard />} />
            <Route path="/upload" element={<CreatorUpload />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
