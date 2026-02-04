# 📚 Murph Frontend - On-Demand Learning Platform

A modern React web app for pay-per-use online courses with AI-powered discovery, real-time session metering, blockchain payments via Finternet sandbox, and AI review validation.

## 🚀 Quick Start

### Prerequisites
- Node.js 20.19+ or 22.12+
- npm 11.6.0+

### Installation

```bash
# Install dependencies
npm install

# Copy environment file and add your API keys
cp .env.example .env.local

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173/`

## 📦 Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🛠️ Tech Stack

- **React 18** + **Vite** (build tool)
- **Tailwind CSS** + **shadcn/ui** (components)
- **React Router** (routing)
- **Zustand** (state management)
- **React Hook Form** + **Zod** (forms)
- **Framer Motion** (animations)
- **Axios** (HTTP client)
- **React Player** (video)
- **Lucide Icons** (icons)
- **Sonner** (toasts)

## 📁 Project Structure

```
src/
├── components/       # Reusable UI components
├── features/         # Auth, payment, session, AI, review logic
├── pages/           # Route pages (Home, Discover, SessionDetail, etc.)
├── hooks/           # Custom hooks
├── lib/             # Utilities & mock data
├── App.js           # Router setup
└── index.css        # Tailwind + global styles
```

## 🎯 Core Features

✅ **Home & Course Discovery** - Grid-based course listings  
✅ **AI Chat Discovery** - Personalized recommendations  
✅ **Session Metering** - Real-time timer + cost calculation  
✅ **Video Player** - Stream courses with progress tracking  
✅ **Review Validation** - AI-powered feedback & bonuses  
✅ **Wallet System** - Balance & transaction history  
✅ **Teacher Dashboard** - Analytics & reviews  
✅ **Course Upload** - Creator interface  

## 🔑 Environment Setup

Copy `.env.example` to `.env.local` and fill in your API keys:

```env
VITE_OPENAI_API_KEY=your-key
VITE_FINTERNET_BASE_URL=sandbox-url
VITE_SUPABASE_URL=optional
```

## 📝 Mock Data

The app works fully with mock data. Replace API calls in feature services when backend is ready.

---

**Built for TSEC Hackathon 2026** ❤️
