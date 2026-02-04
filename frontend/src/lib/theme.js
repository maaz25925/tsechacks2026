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
    background: '#F5F5F7',
    surface: '#FFFFFF',
    text: '#1F2937',
    textSecondary: '#6B7280',
    border: '#E5E7EB',
  },
  dark: {
    background: '#1E3A5F',
    surface: '#2C5282',
    text: '#F1F5F9',
    textSecondary: '#CBD5E1',
    border: '#334155',
  },
};

export const getThemeVariables = (isDark = false) => {
  const mode = isDark ? THEME.dark : THEME.light;
  return {
    '--primary': isDark ? '#60A5FA' : THEME.colors.primary,
    '--secondary': isDark ? '#A78BFA' : THEME.colors.secondary,
    '--accent': isDark ? '#34D399' : THEME.colors.accent,
    '--bg-primary': mode.background,
    '--bg-secondary': mode.surface,
    '--text-primary': mode.text,
    '--text-secondary': mode.textSecondary,
    '--border-color': mode.border,
  };
};

export default THEME;
