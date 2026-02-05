// Mock Users (IDs match backend seeded data)
export const mockUsers = [
  {
    id: "student_1",
    name: "Jamie Chen",
    role: "student",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Jamie",
    balance: 2500,
    totalSpent: 1200,
  },
  {
    id: "teacher_1",
    name: "Aisha Patel",
    role: "teacher",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Aisha",
    balance: 5000,
    totalEarnings: 3400,
  },
  {
    id: "teacher_2",
    name: "Marco Silva",
    role: "teacher",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Marco",
    balance: 5000,
    totalEarnings: 3400,
  },
];

// Mock Courses/Sessions
export const mockSessions = [
  {
    id: "listing_1",
    title: "10-min Morning Meditation Reset",
    instructor: {
      id: "teacher_1",
      name: "Aisha Patel",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Aisha",
    },
    description: "Guided breathing + mindful check-in for busy days.",
    category: "Meditation",
    duration: 10, // minutes
    pricePerMinute: 1.5, // Finternet credits
    rating: 4.8,
    reviews: 124,
    thumbnail: "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400&h=300&fit=crop",
    tags: ["Meditation", "Mindfulness", "Wellness"],
    learningObjectives: [
      "Calm your mind quickly",
      "Use breathing techniques",
      "Start your day centered",
    ],
  },
  {
    id: "listing_2",
    title: "Yoga Flow: Lower Back Relief",
    instructor: {
      id: "teacher_1",
      name: "Aisha Patel",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Aisha",
    },
    description: "Gentle sequence to reduce stiffness and improve mobility.",
    category: "Fitness",
    duration: 18,
    pricePerMinute: 1.8,
    rating: 4.6,
    reviews: 98,
    thumbnail: "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400&h=300&fit=crop",
    tags: ["Yoga", "Fitness", "Mobility"],
    learningObjectives: [
      "Improve lower back flexibility",
      "Reduce pain and stiffness",
      "Learn proper alignment",
    ],
  },
  {
    id: "listing_3",
    title: "Guitar: 3 Chords You Can Use Everywhere",
    instructor: {
      id: "teacher_2",
      name: "Marco Silva",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Marco",
    },
    description: "A quick-start lesson for rhythm guitar (with practice track).",
    category: "Music",
    duration: 15,
    pricePerMinute: 2.0,
    rating: 4.9,
    reviews: 156,
    thumbnail: "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=400&h=300&fit=crop",
    tags: ["Guitar", "Music", "Beginner"],
    learningObjectives: [
      "Learn 3 essential chords",
      "Practice rhythm guitar",
      "Play simple songs",
    ],
  },
  {
    id: "listing_4",
    title: "Advanced Meditation Series",
    instructor: {
      id: "teacher_1",
      name: "Aisha Patel",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Aisha",
    },
    description: "Deep meditation techniques for experienced practitioners.",
    category: "Meditation",
    duration: 45,
    pricePerMinute: 1.2,
    rating: 4.7,
    reviews: 142,
    thumbnail: "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400&h=300&fit=crop",
    tags: ["Meditation", "Advanced", "Mindfulness"],
    learningObjectives: [
      "Master advanced techniques",
      "Deeper meditation",
      "Spiritual growth",
    ],
  },
  {
    id: "listing_5",
    title: "Fingerstyle Guitar Masterclass",
    instructor: {
      id: "teacher_2",
      name: "Marco Silva",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Marco",
    },
    description: "Learn fingerstyle technique and classical guitar patterns.",
    category: "Music",
    duration: 60,
    pricePerMinute: 2.5,
    rating: 4.5,
    reviews: 87,
    thumbnail: "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=400&h=300&fit=crop",
    tags: ["Guitar", "Fingerstyle", "Advanced"],
    learningObjectives: [
      "Fingerstyle technique",
      "Classical patterns",
      "Music theory for guitar",
    ],
  },
];

// Mock Active Sessions (user sessions in progress)
export const mockActiveSessions = [
  {
    id: "active1",
    sessionId: "listing_1",
    userId: "student_1",
    startedAt: new Date(Date.now() - 5 * 60000), // 5 minutes ago
    elapsedMinutes: 5,
    estimatedCost: 7.5,
    sessionTitle: "10-min Morning Meditation Reset",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4",
    progress: 50, // percentage
  },
];

// Mock Reviews & Validations
export const mockReviews = [
  {
    id: "review1",
    sessionId: "listing_1",
    userId: "student_1",
    rating: 5,
    text: "Excellent meditation session!",
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60000),
    aiValidation: { score: 0.95, feedback: "High-quality review" },
    bonus: 25,
  },
  {
    id: "review2",
    sessionId: "listing_1",
    userId: "teacher_1",
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
    amount: -15.0,
    session: "10-min Morning Meditation Reset",
    date: new Date(Date.now() - 1 * 60 * 60000),
    status: "completed",
  },
  {
    id: "tx2",
    type: "earnings",
    amount: 27.0,
    session: "Yoga Flow: Lower Back Relief",
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
  { id: "msg1", type: "user", text: "I want to learn meditation" },
  {
    id: "msg2",
    type: "ai",
    text: "Great! Based on your interests, I recommend the Morning Meditation Reset. It's short, affordable, and perfect for beginners.",
  },
  { id: "msg3", type: "user", text: "What about yoga classes?" },
  {
    id: "msg4",
    type: "ai",
    text: "For yoga, the Lower Back Relief session is excellent. It focuses on mobility and is taught by an experienced instructor!",
  },
];

// Categories for filters
export const mockCategories = [
  "All",
  "Meditation",
  "Fitness",
  "Music",
  "Wellness",
  "Advanced",
  "Beginner",
];
