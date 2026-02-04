// Review validation and bonus calculation service
import { aiService } from '../ai/aiService';

export const reviewService = {
  async submitReview(sessionId, userId, rating, text) {
    // Validate review with AI
    const validation = await aiService.validateReview(text);

    return {
      id: 'review_' + Date.now(),
      sessionId,
      userId,
      rating,
      text,
      aiValidation: validation,
      bonus: validation.bonus,
      createdAt: new Date(),
    };
  },

  calculateBonus(validationScore) {
    // Bonus = 10-50 credits based on validation score
    const baseBonus = 10;
    const maxBonus = 50;
    return Math.floor(baseBonus + (maxBonus - baseBonus) * validationScore);
  },

  getQualityFeedback(score) {
    if (score > 0.9) return 'Excellent review!';
    if (score > 0.8) return 'Great feedback!';
    if (score > 0.7) return 'Good review';
    return 'Review needs improvement';
  },
};
