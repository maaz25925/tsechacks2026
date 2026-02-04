// Session state management with Zustand
import { create } from 'zustand';

export const useSessionStore = create((set) => ({
  activeSession: null,
  elapsedTime: 0,
  estimatedCost: 0,
  isPaused: false,

  startSession: (session) =>
    set({
      activeSession: session,
      elapsedTime: 0,
      estimatedCost: 0,
      isPaused: false,
    }),

  updateElapsedTime: (seconds) =>
    set((state) => ({
      elapsedTime: state.elapsedTime + seconds,
      estimatedCost:
        (state.elapsedTime / 60) * (state.activeSession?.pricePerMinute || 0),
    })),

  pauseSession: () => set({ isPaused: true }),

  resumeSession: () => set({ isPaused: false }),

  endSession: () =>
    set({
      activeSession: null,
      elapsedTime: 0,
      estimatedCost: 0,
    }),
}));

// Context-based provider for optional use
import { createContext } from 'react';

export const SessionContext = createContext();

export const SessionProvider = ({ children }) => {
  const sessionStore = useSessionStore();

  return (
    <SessionContext.Provider value={sessionStore}>
      {children}
    </SessionContext.Provider>
  );
};
