// Theme Configuration
// Primary: '#3B82F6' (Blue)
// Secondary: '#8B5CF6' (Purple)
// Accent: '#10B981' (Green)

export const THEME = {
  colors: {
    primary: '#3B82F6',
    secondary: '#8B5CF6',
    accent: '#10B981',
  },
  light: {
    background: '#FFFFFF',
    surface: '#F9FAFB',
    text: '#1F2937',
    textSecondary: '#6B7280',
    border: '#E5E7EB',
  },
  dark: {
    background: '#0F172A',
    surface: '#1E293B',
    text: '#F1F5F9',
    textSecondary: '#CBD5E1',
    border: '#334155',
  },
};

export const getThemeVariables = (isDark = false) => {
  const mode = isDark ? THEME.dark : THEME.light;
  return {
    '--primary': THEME.colors.primary,
    '--secondary': THEME.colors.secondary,
    '--accent': THEME.colors.accent,
    '--bg-primary': mode.background,
    '--bg-secondary': mode.surface,
    '--text-primary': mode.text,
    '--text-secondary': mode.textSecondary,
    '--border-color': mode.border,
  };
};

export default THEME;
