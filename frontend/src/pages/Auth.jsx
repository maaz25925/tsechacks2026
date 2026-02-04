import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthProvider.jsx';
import { Mail, Lock, User, Briefcase, MessageSquare } from 'lucide-react';
import './Auth.css';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    bio: '',
    role: 'student',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  
  const { login, register, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setFormError('');
    clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setIsSubmitting(true);

    if (!formData.email || !formData.password) {
      setFormError('Email and password are required');
      setIsSubmitting(false);
      return;
    }

    if (!isLogin && !formData.name) {
      setFormError('Name is required');
      setIsSubmitting(false);
      return;
    }

    let result;
    if (isLogin) {
      result = await login(formData.email, formData.password);
    } else {
      result = await register({
        email: formData.email,
        password: formData.password,
        name: formData.name,
        bio: formData.bio || null,
        role: formData.role,
      });
    }

    setIsSubmitting(false);

    if (result.success) {
      navigate('/home');
    } else {
      setFormError(result.error);
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setFormError('');
    clearError();
    setFormData({
      email: '',
      password: '',
      name: '',
      bio: '',
      role: 'student',
    });
  };

  return (
    <div className="auth-page">
      <div className="auth-wrapper">
        {/* Left side - Branding */}
        <div className="auth-branding">
          <div className="branding-content">
            <div className="branding-logo">
              <div className="logo-shape">M</div>
            </div>
            <h1 className="branding-title">Murph</h1>
            <p className="branding-subtitle">Learn from the best instructors</p>
            <p className="branding-description">
              Connect with expert teachers and learn skills at your own pace. Join thousands of learners today.
            </p>
          </div>
        </div>

        {/* Right side - Form */}
        <div className="auth-form-wrapper">
          <div className="auth-form-container">
            <div className="auth-header">
              <div className="auth-tabs">
                <button 
                  className={`auth-tab ${isLogin ? 'active' : ''}`}
                  onClick={() => switchMode()}
                >
                  Sign In
                </button>
                <button 
                  className={`auth-tab ${!isLogin ? 'active' : ''}`}
                  onClick={() => switchMode()}
                >
                  Sign Up
                </button>
              </div>
            </div>

            <form className="auth-form" onSubmit={handleSubmit}>
              {(formError || error) && (
                <div className="auth-error">
                  <span>{String(formError || error)}</span>
                </div>
              )}

              {!isLogin && (
                <div className="form-group">
                  <label htmlFor="name">Full Name</label>
                  <div className="input-wrapper">
                    {/* <User size={18} className="input-icon" /> */}
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="John Doe"
                      className="form-input"
                    />
                  </div>
                </div>
              )}

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <div className="input-wrapper">
                  {/* <Mail size={18} className="input-icon" /> */}
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="you@example.com"
                    className="form-input"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <div className="input-wrapper">
                  {/* <Lock size={18} className="input-icon" /> */}
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="form-input"
                    required
                    minLength="6"
                  />
                </div>
                <small className="form-hint">Minimum 6 characters</small>
              </div>



              <button 
                type="submit" 
                className="auth-submit-btn"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <span className="loading-spinner"></span>
                ) : (
                  isLogin ? 'Sign In' : 'Create Account'
                )}
              </button>
            </form>

            <div className="auth-footer">
              <p>
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button 
                  type="button" 
                  className="auth-switch-btn"
                  onClick={switchMode}
                >
                  {isLogin ? 'Sign Up' : 'Sign In'}
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
