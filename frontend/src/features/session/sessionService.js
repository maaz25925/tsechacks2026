import api from '../../features/auth/authService';

export const sessionService = {
  /**
   * Start a new session
   * Creates a session and locks funds via Finternet
   */
  async startSession({ studentId, listingId, reserveAmount }) {
    try {
      const payload = {
        student_id: studentId,
        listing_id: listingId,
      };
      if (reserveAmount !== undefined) {
        payload.reserve_amount = reserveAmount;
      }
      
      const response = await api.post('/sessions/start', payload);
      console.log('Session started:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to start session:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * End an active session
   * Computes final charge, refund, and settles payment
   */
  async endSession({ sessionId, completionPercentage, engagementMetrics }) {
    try {
      const payload = {
        session_id: sessionId,
      };
      if (completionPercentage !== undefined) {
        payload.completion_percentage = completionPercentage;
      }
      if (engagementMetrics) {
        payload.engagement_metrics = engagementMetrics;
      }

      const response = await api.post('/sessions/end', payload);
      console.log('Session ended:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to end session:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * Get session details
   */
  async getSession(sessionId) {
    try {
      const response = await api.get(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get session:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * List recent sessions for a student
   */
  async getStudentSessions(studentId) {
    try {
      const response = await api.get(`/sessions/student/${studentId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get student sessions:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * List recent sessions for a teacher
   */
  async getTeacherSessions(teacherId) {
    try {
      const response = await api.get(`/sessions/teacher/${teacherId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get teacher sessions:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * Get video URLs for an active session
   */
  async getSessionVideos(sessionId) {
    try {
      const response = await api.get(`/sessions/${sessionId}/videos`);
      return response.data;
    } catch (error) {
      console.error('Failed to get session videos:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * Get payment records for a session
   */
  async getSessionPayments(sessionId) {
    try {
      const response = await api.get(`/payments/by_session?session_id=${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get session payments:', error.response?.data || error.message);
      throw error;
    }
  },
};

export default sessionService;
