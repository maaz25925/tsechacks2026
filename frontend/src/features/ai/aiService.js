// AI Service for discovery chat and review validation
import axios from 'axios';

const AI_BASE_URL = import.meta.env.VITE_OPENAI_BASE_URL || 'https://api.openai.com/v1';
const AI_KEY = import.meta.env.VITE_OPENAI_API_KEY || 'mock-key';

export const aiService = {
  async discoverCourse(userMessage) {
    // Mock AI discovery response
    const responses = [
      'Based on your interest, I recommend the React Hooks Masterclass!',
      'You might enjoy the Node.js Backend Development session.',
      'Data Science courses are trending. Try Python Data Analysis!',
    ];
    return {
      message: responses[Math.floor(Math.random() * responses.length)],
      suggestedSessions: [],
    };
  },

  async validateReview(reviewText) {
    // Mock validation response
    return {
      score: Math.random() * 0.3 + 0.7, // 0.7-1.0
      feedback: 'Well-written review with constructive feedback',
      bonus: Math.floor(Math.random() * 25) + 10,
    };
  },

  async callOpenAI(messages) {
    // Mock OpenAI call for real implementation
    if (!AI_KEY || AI_KEY === 'mock-key') {
      return 'Mock AI response. Connect your OpenAI API key to enable real AI.';
    }
    // Real implementation would call OpenAI API here
    return 'AI response from OpenAI';
  },

  async callGroq(messages) {
    // Alternative LLM provider
    return 'Mock Groq response';
  },
};
