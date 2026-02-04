# Theme System Documentation

## Overview
This application uses a centralized theme system with CSS custom properties (variables) that enables seamless switching between light and dark modes across the entire app.

## Color Palette
- **Primary**: `#3B82F6` (Blue)
- **Secondary**: `#8B5CF6` (Purple)  
- **Accent**: `#10B981` (Green)

## Available CSS Variables

### Primary Colors
- `--primary`: Primary color (#3B82F6)
- `--secondary`: Secondary color (#8B5CF6)
- `--accent`: Accent color (#10B981)

### Light Mode (Default)
- `--bg-primary`: #FFFFFF (Main background)
- `--bg-secondary`: #F9FAFB (Secondary background)
- `--text-primary`: #1F2937 (Main text)
- `--text-secondary`: #6B7280 (Secondary text)
- `--border-color`: #E5E7EB (Borders)

### Dark Mode
- `--bg-primary`: #0F172A (Main background)
- `--bg-secondary`: #1E293B (Secondary background)
- `--text-primary`: #F1F5F9 (Main text)
- `--text-secondary`: #CBD5E1 (Secondary text)
- `--border-color`: #334155 (Borders)

## How to Use

### Styling with Theme Variables
Instead of hardcoding colors, use CSS custom properties in your stylesheets:

```css
.my-component {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.my-button {
  background-color: var(--primary);
  color: white;
}
```

### Using the useTheme Hook
To access theme state and toggle functionality in React components:

```jsx
import { useTheme } from './features/theme/ThemeProvider.jsx';

function MyComponent() {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme}>
      Switch to {isDarkMode ? 'Light' : 'Dark'} Mode
    </button>
  );
}
```

## File Structure
- `src/styles/theme.css` - Theme CSS custom properties and utilities
- `src/lib/theme.js` - Theme configuration (colors, values)
- `src/features/theme/ThemeProvider.jsx` - React context for theme management
- All component CSS files use `var(--colorName)` instead of hardcoded colors

## How Theme Switching Works
1. **Initialization**: On app load, the system checks localStorage for saved preference, otherwise uses system preference
2. **Storage**: User's choice is saved to localStorage as `theme: 'light' | 'dark'`
3. **Application**: `data-theme` attribute is set on the document root
4. **CSS**: CSS rules under `[data-theme="dark"]` apply dark mode colors

## Adding New Components
When creating new components:
1. Create the component as usual
2. In the CSS file, use theme variables:
   - `background-color: var(--bg-primary);`
   - `color: var(--text-primary);`
   - `border-color: var(--border-color);`
3. Add transitions for smooth theme switching:
   - `transition: background-color 0.3s ease, color 0.3s ease;`

## Changing the Theme
To change global colors or add new shades, edit:
- `src/styles/theme.css` - For CSS custom properties
- `src/lib/theme.js` - For JavaScript-accessible values

Changes in these files automatically affect the entire application!
