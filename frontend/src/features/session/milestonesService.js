import api from '../../features/auth/authService';

export const milestonesService = {
  /**
   * Create a payment intent for milestone-based payouts
   * Returns: { intent_id, escrow_id, status, total_amount }
   */
  async createPaymentIntent({ amount, currency = 'USD', description, metadata }) {
    try {
      const payload = {
        amount,
        currency,
        description,
      };
      if (metadata) {
        payload.metadata = metadata;
      }

      const response = await api.post('/milestones/intent', payload);
      console.log('Payment intent created:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to create payment intent:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * Get escrow details by intent ID
   * First tries DB, falls back to Finternet API
   */
  async getEscrow(intentId) {
    try {
      const response = await api.get(`/milestones/escrow/${intentId}`);
      console.log('Escrow details:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to get escrow:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * Create a milestone tied to an escrow and session
   * Used in a loop as user engages content
   */
  async createMilestone({ escrowId, sessionId, index, description, amount, percentage }) {
    try {
      const payload = {
        escrow_id: escrowId,
        session_id: sessionId,
        index,
        description,
        amount,
        percentage,
      };

      const response = await api.post('/milestones', payload);
      console.log('Milestone created:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to create milestone:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * Get milestone details
   */
  async getMilestone(milestoneId) {
    try {
      const response = await api.get(`/milestones/${milestoneId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get milestone:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * List milestones filtered by escrow or session
   */
  async listMilestones({ escrowId, sessionId, limit = 10, offset = 0 }) {
    try {
      const params = new URLSearchParams();
      if (escrowId) params.append('escrow_id', escrowId);
      if (sessionId) params.append('session_id', sessionId);
      params.append('limit', limit);
      params.append('offset', offset);

      const response = await api.get(`/milestones?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Failed to list milestones:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * Submit proof for a milestone (video URL)
   * This automatically completes the milestone and triggers fund release to teacher
   */
  async submitProof(milestoneId, { videoUrl, notes }) {
    try {
      const payload = {
        video_url: videoUrl,
        notes,
      };

      const response = await api.post(
        `/milestones/${milestoneId}/proof`,
        payload
      );
      console.log('Proof submitted:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to submit proof:', error.response?.data || error.message);
      throw error;
    }
  },

  /**
   * Manual completion fallback (rarely used)
   */
  async completeMilestone(milestoneId) {
    try {
      const response = await api.post(`/milestones/${milestoneId}/complete`);
      console.log('Milestone completed:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to complete milestone:', error.response?.data || error.message);
      throw error;
    }
  },
};

export default milestonesService;
