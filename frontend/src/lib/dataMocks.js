// Mock Users
export const mockUsers = [
  {
    id: "user1",
    name: "Alice Johnson",
    role: "student",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice",
    balance: 2500,
    totalSpent: 1200,
  },
  {
    id: "user2",
    name: "Bob Smith",
    role: "teacher",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob",
    balance: 5000,
    totalEarnings: 3400,
  },
  {
    id: "user3",
    name: "Carol White",
    role: "student",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Carol",
    balance: 1800,
    totalSpent: 800,
  },
];

// Mock Courses/Sessions
export const mockSessions = [
  {
    id: "session1",
    title: "React Hooks Masterclass",
    instructor: {
      id: "user2",
      name: "Bob Smith",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob",
    },
    description: "Deep dive into React Hooks: useState, useEffect, useContext, and custom hooks.",
    category: "Web Development",
    duration: 90, // minutes
    pricePerMinute: 0.5, // Finternet credits
    rating: 4.8,
    reviews: 124,
    thumbnail: "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=400&h=300&fit=crop",
    tags: ["React", "JavaScript", "Hooks"],
    learningObjectives: [
      "Master React Hooks API",
      "Build custom hooks",
      "Understand closure patterns",
    ],
  },
  {
    id: "session2",
    title: "Python Data Analysis",
    instructor: {
      id: "user3",
      name: "Carol White",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Carol",
    },
    description: "Learn pandas, numpy, and data visualization with Python.",
    category: "Data Science",
    duration: 120,
    pricePerMinute: 0.3,
    rating: 4.6,
    reviews: 98,
    thumbnail: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
    tags: ["Python", "Data Science", "Analytics"],
    learningObjectives: [
      "Data manipulation with pandas",
      "NumPy fundamentals",
      "Create insightful visualizations",
    ],
  },
  {
    id: "session3",
    title: "Web Design Fundamentals",
    instructor: {
      id: "user2",
      name: "Bob Smith",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob",
    },
    description: "UI/UX principles, design systems, and CSS mastery.",
    category: "Design",
    duration: 75,
    pricePerMinute: 0.4,
    rating: 4.9,
    reviews: 156,
    thumbnail: "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=300&fit=crop",
    tags: ["Design", "CSS", "UI/UX"],
    learningObjectives: [
      "Design system principles",
      "Advanced CSS techniques",
      "Responsive design",
    ],
  },
  {
    id: "session4",
    title: "Node.js Backend Development",
    instructor: {
      id: "user1",
      name: "Alice Johnson",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice",
    },
    description: "Build scalable APIs with Express, authentication, and databases.",
    category: "Backend",
    duration: 110,
    pricePerMinute: 0.6,
    rating: 4.7,
    reviews: 142,
    thumbnail: "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=300&fit=crop",
    tags: ["Node.js", "Backend", "APIs"],
    learningObjectives: [
      "REST API design",
      "Authentication & authorization",
      "Database integration",
    ],
  },
  {
    id: "session5",
    title: "Machine Learning Essentials",
    instructor: {
      id: "user3",
      name: "Carol White",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Carol",
    },
    description: "Introduction to ML models, scikit-learn, and TensorFlow.",
    category: "AI/ML",
    duration: 150,
    pricePerMinute: 0.8,
    rating: 4.5,
    reviews: 87,
    thumbnail: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=300&fit=crop",
    tags: ["ML", "AI", "Python"],
    learningObjectives: [
      "Supervised learning algorithms",
      "Model evaluation",
      "Feature engineering",
    ],
  },
  {
    id: "session6",
    title: "Docker & Kubernetes Basics",
    instructor: {
      id: "user2",
      name: "Bob Smith",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob",
    },
    description: "Containerization, orchestration, and DevOps essentials.",
    category: "DevOps",
    duration: 100,
    pricePerMinute: 0.55,
    rating: 4.4,
    reviews: 76,
    thumbnail: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=300&fit=crop",
    tags: ["Docker", "Kubernetes", "DevOps"],
    learningObjectives: [
      "Container basics",
      "Kubernetes orchestration",
      "CI/CD pipelines",
    ],
  },
];

// Mock Active Sessions (user sessions in progress)
export const mockActiveSessions = [
  {
    id: "active1",
    sessionId: "session1",
    userId: "user1",
    startedAt: new Date(Date.now() - 15 * 60000), // 15 minutes ago
    elapsedMinutes: 15,
    estimatedCost: 7.5,
    sessionTitle: "React Hooks Masterclass",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4",
    progress: 25, // percentage
  },
];

// Mock Reviews & Validations
export const mockReviews = [
  {
    id: "review1",
    sessionId: "session1",
    userId: "user1",
    rating: 5,
    text: "Excellent explanation of closures and hooks!",
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60000),
    aiValidation: { score: 0.95, feedback: "High-quality review" },
    bonus: 25,
  },
  {
    id: "review2",
    sessionId: "session1",
    userId: "user3",
    rating: 4,
    text: "Very comprehensive, could use more examples.",
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60000),
    aiValidation: { score: 0.87, feedback: "Constructive feedback" },
    bonus: 15,
  },
];

// Mock Wallet Transactions
export const mockTransactions = [
  {
    id: "tx1",
    type: "purchase",
    amount: -7.5,
    session: "React Hooks Masterclass",
    date: new Date(Date.now() - 1 * 60 * 60000),
    status: "completed",
  },
  {
    id: "tx2",
    type: "earnings",
    amount: 45.2,
    session: "Web Design Fundamentals",
    date: new Date(Date.now() - 2 * 24 * 60 * 60000),
    status: "completed",
  },
  {
    id: "tx3",
    type: "bonus",
    amount: 15,
    reason: "Review bonus",
    date: new Date(Date.now() - 3 * 24 * 60 * 60000),
    status: "completed",
  },
];

// Mock AI Chat History
export const mockChatMessages = [
  { id: "msg1", type: "user", text: "I want to learn React" },
  {
    id: "msg2",
    type: "ai",
    text: "Great! Based on your learning style, I recommend starting with React Hooks Masterclass. It's highly rated and affordable.",
  },
  { id: "msg3", type: "user", text: "What about backend development?" },
  {
    id: "msg4",
    type: "ai",
    text: "For backend, Node.js Backend Development is perfect. It covers APIs, authentication, and databases - exactly what you need!",
  },
];

// Categories for filters
export const mockCategories = [
  "All",
  "Web Development",
  "Data Science",
  "Design",
  "Backend",
  "AI/ML",
  "DevOps",
];
