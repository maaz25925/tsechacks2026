import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './features/theme/ThemeProvider.jsx';
import Layout from './components/Layout.jsx';
import Home from './pages/Home.jsx';
import Discover from './pages/Discover.jsx';
import SessionDetail from './pages/SessionDetail.jsx';
import ActiveSession from './pages/ActiveSession.jsx';
import Summary from './pages/Summary.jsx';
import Wallet from './pages/Wallet.jsx';
import TeacherDashboard from './pages/TeacherDashboard.jsx';
import CreatorUpload from './pages/CreatorUpload.jsx';
import './styles/theme.css';
import './App.css';

function AppContent() {
  return (
    <Router>
      <div className="app-wrapper">
        <Layout>
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
        </Layout>
      </div>
    </Router>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
