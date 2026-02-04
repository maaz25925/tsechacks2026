import { useState } from 'react';
import { Star, Send } from 'lucide-react';
import { reviewService } from '../features/review/reviewService';
import './ReviewForm.css';

export default function ReviewForm({ sessionId, onSubmit }) {
  const [rating, setRating] = useState(0);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0 || !text.trim()) return;

    setLoading(true);
    try {
      const review = await reviewService.submitReview(
        sessionId,
        'user1',
        rating,
        text
      );
      onSubmit(review);
      setRating(0);
      setText('');
    } catch (error) {
      console.error('Review submission failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="review-form">
      <h3>Rate this Session</h3>

      <div className="star-rating">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
            className={`star ${star <= rating ? 'active' : ''}`}
          >
            <Star size={32} fill={star <= rating ? '#fbbf24' : 'none'} />
          </button>
        ))}
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Share your feedback... (AI will validate and award bonus credits)"
        className="review-textarea"
        rows="4"
      />

      <div className="review-footer">
        <p className="review-hint">
          📝 High-quality reviews earn 10-50 bonus credits!
        </p>
        <button
          onClick={handleSubmit}
          disabled={rating === 0 || !text.trim() || loading}
          className="submit-btn"
        >
          <Send size={18} />
          Submit Review
        </button>
      </div>
    </div>
  );
}
