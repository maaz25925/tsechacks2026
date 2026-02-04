// Auth provider with FastAPI backend integration
import { createContext, useState, useEffect, useContext } from 'react';
import { authService } from './authService.js';

export const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = authService.getStoredUser();
    const storedToken = authService.getStoredToken();
    
    if (storedUser && storedToken) {
      authService.setAuthToken(storedToken);
      setUser(storedUser);
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const login = async (email, password) => {
    setError(null);
    setIsLoading(true);
    try {
      const response = await authService.login({ email, password });
      const userData = {
        id: response.user_id,
        email,
        role: response.role,
      };
      
      authService.setAuthToken(response.access_token);
      authService.storeUser(userData);
      setUser(userData);
      setIsAuthenticated(true);
      return { success: true };
    } catch (err) {
      let message = 'Login failed. Please try again.';
      
      if (err.response?.data?.detail) {
        message = err.response.data.detail;
      } else if (err.response?.data?.error?.message) {
        message = err.response.data.error.message;
      } else if (err.response?.status === 401) {
        message = 'Invalid email or password. Please check your credentials.';
      } else if (err.message) {
        message = err.message;
      }
      
      console.error('Login error:', err.response?.data || err.message);
      setError(message);
      return { success: false, error: message };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async ({ email, password, role, name, bio }) => {
    setError(null);
    setIsLoading(true);
    try {
      const response = await authService.register({ email, password, role, name, bio });
      const userData = {
        id: response.user_id,
        email,
        name,
        role: response.role,
        bio,
      };
      
      authService.setAuthToken(response.access_token);
      authService.storeUser(userData);
      setUser(userData);
      setIsAuthenticated(true);
      return { success: true };
    } catch (err) {
      let message = 'Registration failed. Please try again.';
      
      if (err.response?.data?.detail) {
        message = err.response.data.detail;
      } else if (err.response?.data?.error?.message) {
        message = err.response.data.error.message;
      } else if (err.message) {
        message = err.message;
      }
      
      console.error('Register error details:', err);
      setError(message);
      return { success: false, error: message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.clearStorage();
    authService.setAuthToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider value={{ 
      user, 
      isAuthenticated, 
      isLoading, 
      error, 
      login, 
      register, 
      logout,
      clearError 
    }}>
      {children}
    </AuthContext.Provider>
  );
};
