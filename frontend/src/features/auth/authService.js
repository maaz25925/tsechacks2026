// Auth API service for FastAPI backend
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authService = {
  async register({ email, password, role, name, bio }) {
    try {
      const payload = {
        email: email.toLowerCase().trim(),
        password,
        role: (role || 'student').toLowerCase(),
        name: name.trim(),
        bio: bio && bio.trim() ? bio.trim() : null,
      };
      console.log('Register payload:', payload);
      const response = await api.post('/auth/register', payload);
      return response.data;
    } catch (error) {
      console.error('Register error:', error.response?.data || error.message);
      throw error;
    }
  },

  async login({ email, password }) {
    try {
      const payload = { 
        email: email.toLowerCase().trim(),
        password 
      };
      console.log('Login attempt with:', { email: payload.email });
      const response = await api.post('/auth/login', payload);
      return response.data;
    } catch (error) {
      console.error('=== LOGIN ERROR DEBUG ===');
      console.error('Error type:', typeof error);
      console.error('Error constructor:', error?.constructor?.name);
      console.error('Error message:', error?.message);
      console.error('Error status:', error?.response?.status);
      console.error('Error data:', error?.response?.data);
      console.error('Full error:', error);
      if (error?.response?.data) {
        try {
          console.error('Error data stringified:', JSON.stringify(error.response.data));
        } catch(e) {
          console.error('Could not stringify error data');
        }
      }
      console.error('========================');
      throw error;
    }
  },

  setAuthToken(token) {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('access_token', token);
    } else {
      delete api.defaults.headers.common['Authorization'];
      localStorage.removeItem('access_token');
    }
  },

  getStoredToken() {
    return localStorage.getItem('access_token');
  },

  getStoredUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  storeUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  },

  clearStorage() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};

export default api;
