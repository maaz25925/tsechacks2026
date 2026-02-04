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

/**
 * AI-powered search function
 * Takes a user query and returns an AI-generated summary with related suggestions
 */
export async function askAI(query) {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1200));

  // Mock AI responses based on keywords
  const lowerQuery = query.toLowerCase();

  // React-related queries
  if (lowerQuery.includes('react') || lowerQuery.includes('hooks') || lowerQuery.includes('component')) {
    return {
      summary: `React is a powerful JavaScript library for building user interfaces. Based on your query about "${query}", I found comprehensive sessions covering modern React patterns, hooks like useState and useEffect, component composition, and state management. These sessions are suitable for both beginners looking to understand core concepts and experienced developers wanting to learn advanced patterns.`,
      suggestions: [
        'React Hooks deep dive (useState, useEffect, useContext)',
        'Component architecture and best practices',
        'State management with Redux or Zustand',
        'Performance optimization techniques',
      ],
    };
  }

  // Backend/Node.js queries
  if (lowerQuery.includes('backend') || lowerQuery.includes('node') || lowerQuery.includes('api') || lowerQuery.includes('server')) {
    return {
      summary: `Backend development encompasses server-side programming, API design, and database management. For "${query}", I've identified sessions covering RESTful API design, authentication strategies, database integration with MongoDB and PostgreSQL, and modern backend frameworks like Express.js and Fastify. These materials will help you build scalable and secure server applications.`,
      suggestions: [
        'RESTful API design principles',
        'Authentication with JWT and OAuth',
        'Database modeling and optimization',
        'Microservices architecture patterns',
      ],
    };
  }

  // Python/Data Science queries
  if (lowerQuery.includes('python') || lowerQuery.includes('data') || lowerQuery.includes('machine learning') || lowerQuery.includes('ai')) {
    return {
      summary: `Python is the leading language for data science and machine learning. Regarding "${query}", I found sessions covering data analysis with pandas and NumPy, visualization with matplotlib and seaborn, machine learning fundamentals with scikit-learn, and deep learning with TensorFlow and PyTorch. These courses cater to aspiring data scientists and ML engineers.`,
      suggestions: [
        'Python fundamentals for data science',
        'Data visualization and exploratory analysis',
        'Machine learning algorithms and applications',
        'Deep learning and neural networks',
      ],
    };
  }

  // Web development queries
  if (lowerQuery.includes('web') || lowerQuery.includes('frontend') || lowerQuery.includes('css') || lowerQuery.includes('html')) {
    return {
      summary: `Modern web development requires knowledge of HTML, CSS, JavaScript, and various frameworks. For your query "${query}", I've curated sessions on responsive design, CSS Grid and Flexbox, modern JavaScript (ES6+), accessibility best practices, and framework comparisons. These resources will help you create beautiful, accessible, and performant web applications.`,
      suggestions: [
        'Responsive design with CSS Grid and Flexbox',
        'Modern JavaScript features and patterns',
        'Web accessibility (a11y) fundamentals',
        'Progressive Web Apps (PWAs)',
      ],
    };
  }

  // General/fallback response
  return {
    summary: `I found several relevant educational sessions related to "${query}". These materials cover fundamental concepts, practical applications, and advanced techniques. Browse through the related sessions below to find content that matches your learning goals. Each session includes detailed descriptions, difficulty levels, and ratings from previous learners.`,
    suggestions: [
      'Explore related beginner-friendly tutorials',
      'Check out advanced topics in this area',
      'Review practical project-based sessions',
      'Join live Q&A sessions with experts',
    ],
  };
}
