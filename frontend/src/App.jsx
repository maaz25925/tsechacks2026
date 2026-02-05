import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './features/theme/ThemeProvider.jsx';
import { AuthProvider, useAuth } from './features/auth/AuthProvider.jsx';
import Layout from './components/Layout.jsx';
import Auth from './pages/Auth.jsx';
import Home from './pages/Home.jsx';
import Discover from './pages/Discover.jsx';
import SessionDetail from './pages/SessionDetail.jsx';
import ActiveSession from './pages/ActiveSession.jsx';
import Summary from './pages/Summary.jsx';
import PaymentSuccess from './pages/PaymentSuccess.jsx';
import Wallet from './pages/Wallet.jsx';
import TeacherDashboard from './pages/TeacherDashboard.jsx';
import CreatorUpload from './pages/CreatorUpload.jsx';
import SearchResults from './pages/SearchResults.jsx';
import ChatSearch from './pages/ChatSearch.jsx';
import './styles/theme.css';
import './App.css';

// Protected route wrapper
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner-large"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return children;
}

// Public route - redirect to home if already authenticated
function PublicRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner-large"></div>
      </div>
    );
  }
  
  if (isAuthenticated) {
    return <Navigate to="/home" replace />;
  }
  
  return children;
}

function AppContent() {
  return (
    <Router>
      <div className="app-wrapper">
        <Routes>
          {/* Public auth route */}
          <Route path="/" element={
            <PublicRoute>
              <Auth />
            </PublicRoute>
          } />
          
          {/* Protected routes with Layout */}
          <Route path="/home" element={
            <ProtectedRoute>
              <Layout><Home /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/discover" element={
            <ProtectedRoute>
              <Layout><Discover /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/session/:id" element={
            <ProtectedRoute>
              <Layout><SessionDetail /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/active-session/:id" element={
            <ProtectedRoute>
              <Layout><ActiveSession /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/summary/:sessionId" element={
            <ProtectedRoute>
              <Layout><Summary /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/payment-success" element={
            <ProtectedRoute>
              <PaymentSuccess />
            </ProtectedRoute>
          } />
          <Route path="/wallet" element={
            <ProtectedRoute>
              <Layout><Wallet /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Layout><TeacherDashboard /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/upload" element={
            <ProtectedRoute>
              <Layout><CreatorUpload /></Layout>
            </ProtectedRoute>
          } />
          
          {/* Catch all - redirect to home or auth */}
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/search" element={<ProtectedRoute><SearchResults /></ProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><ChatSearch /></ProtectedRoute>} />
        </Routes>
      </div>
    </Router>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
