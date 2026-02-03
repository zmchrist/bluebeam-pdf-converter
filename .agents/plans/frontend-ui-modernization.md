# Feature: Frontend UI Modernization

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files etc.

## Feature Description

Transform the frontend from a basic light-only theme to a modern, sleek design featuring:
- **Deep blue/purple gradient** color scheme
- **Glass morphism** effects (frosted glass, backdrop blur, soft shadows)
- **Automatic dark/light mode** based on system preferences (`prefers-color-scheme`)

The redesign maintains all existing functionality while dramatically improving visual appeal and adding system-aware theming.

## User Story

As a user of the Bluebeam PDF Map Converter
I want a modern, visually appealing interface that respects my system theme preference
So that I have a pleasant experience using the tool and can work comfortably in any lighting condition

## Problem Statement

The current frontend uses a basic light-only theme with minimal visual distinction. It lacks:
- Dark mode support for users who prefer dark interfaces
- Modern visual effects that communicate quality and professionalism
- A distinctive design that sets the tool apart

## Solution Statement

Implement a comprehensive UI refresh that:
1. Enables Tailwind CSS dark mode with `media` strategy (automatic system preference detection)
2. Adds a gradient mesh background transitioning from deep blue to purple
3. Applies glass morphism to all cards and panels (backdrop blur, transparency, subtle borders)
4. Updates all components with proper dark mode variants
5. Adds modern touches: gradient buttons, soft shadows, glow effects

## Feature Metadata

**Feature Type**: Enhancement
**Estimated Complexity**: Medium
**Primary Systems Affected**: Frontend React components, Tailwind CSS configuration
**Dependencies**: None (all utilities available in Tailwind CSS 3.4.0)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - MUST READ BEFORE IMPLEMENTING

| File | Lines | Why |
|------|-------|-----|
| `frontend/tailwind.config.js` | All | Current theme config, will add darkMode and extend |
| `frontend/src/index.css` | All | Global styles, will add CSS variables and utilities |
| `frontend/src/lib/utils.ts` | All | `cn()` utility function pattern for class merging |
| `frontend/src/components/ui/Button.tsx` | All | Button variant pattern to follow/extend |
| `frontend/src/components/ui/Card.tsx` | All | Compound component pattern (Card.Header, Card.Body) |
| `frontend/src/components/ui/Alert.tsx` | All | Variant config object pattern |
| `frontend/src/components/ui/Spinner.tsx` | All | Size variant pattern |
| `frontend/src/components/layout/Layout.tsx` | All | Root layout structure |
| `frontend/src/components/layout/Header.tsx` | All | Header styling |
| `frontend/src/components/layout/Footer.tsx` | All | Footer styling |
| `frontend/src/features/upload/components/DropZone.tsx` | All | Conditional state-based styling pattern |
| `frontend/src/features/upload/components/FileInfo.tsx` | All | Success state card styling |
| `frontend/src/features/convert/components/ConversionPanel.tsx` | All | Card usage pattern |
| `frontend/src/features/convert/components/DirectionSelector.tsx` | All | Radio button styling with rings |
| `frontend/src/features/convert/components/ProgressDisplay.tsx` | All | Step indicator colors |
| `frontend/src/features/download/components/DownloadButton.tsx` | All | Styled anchor pattern |
| `frontend/src/App.tsx` | All | Main app structure, text colors |

### New Files to Create

None - all changes are modifications to existing files.

### Relevant Documentation

- [Tailwind CSS Dark Mode](https://tailwindcss.com/docs/dark-mode) - Configuration and usage
- [Tailwind CSS Backdrop Blur](https://tailwindcss.com/docs/backdrop-blur) - Glass morphism utilities
- [Tailwind CSS Gradients](https://tailwindcss.com/docs/gradient-color-stops) - Gradient backgrounds

### Patterns to Follow

**Class Merging with cn():**
```typescript
import { cn } from '../../lib/utils';
className={cn(baseClasses, conditionalClasses, props.className)}
```

**Variant Configuration Object (from Alert.tsx):**
```typescript
const variantConfig = {
  success: { bg: 'bg-green-50', border: 'border-green-200', ... },
  error: { bg: 'bg-red-50', ... },
};
```

**Compound Component Pattern (from Card.tsx):**
```typescript
Card.Header = function CardHeader({ children, className }) { ... };
Card.Body = function CardBody({ children, className }) { ... };
```

**Dark Mode Class Pattern:**
```typescript
// Always pair light and dark variants
'bg-white dark:bg-gray-900'
'text-gray-900 dark:text-gray-100'
'border-gray-200 dark:border-gray-700'
```

---

## IMPLEMENTATION PLAN

### Phase 1: Foundation (Tailwind Config + Global CSS)

Set up dark mode, custom utilities, and gradient background infrastructure.

**Tasks:**
- Enable dark mode with `media` strategy
- Add custom shadow utilities for glass effects
- Create mesh gradient CSS utility
- Update body styles for dark mode

### Phase 2: Layout Components

Apply gradient background and glass morphism to the main layout shell.

**Tasks:**
- Add gradient mesh background to Layout
- Convert Header to glass morphism with dark mode
- Update Footer with dark mode support

### Phase 3: Core UI Components

Update all reusable UI components with dark mode variants and modern styling.

**Tasks:**
- Update Card with glass variant and dark mode
- Update Button with gradient primary and dark mode
- Update Alert variants for dark mode
- Update Spinner colors for dark mode

### Phase 4: Feature Components

Apply dark mode to all feature-specific components.

**Tasks:**
- Update DropZone with glass effect and dark mode
- Update FileInfo with dark mode
- Update ConversionPanel with dark mode
- Update DirectionSelector with dark mode
- Update ProgressDisplay with dark mode
- Update DownloadButton with gradient and dark mode
- Update App.tsx text colors for dark mode

---

## STEP-BY-STEP TASKS

### Task 1: UPDATE `frontend/tailwind.config.js`

Enable dark mode and add custom theme extensions.

**IMPLEMENT:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'media',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.1)',
        'glass-lg': '0 16px 48px rgba(0, 0, 0, 0.15)',
        'glow': '0 0 20px rgba(139, 92, 246, 0.3)',
        'glow-lg': '0 0 40px rgba(139, 92, 246, 0.4)',
      },
    },
  },
  plugins: [],
}
```

**VALIDATE:** `cd frontend && npm run build`

---

### Task 2: UPDATE `frontend/src/index.css`

Add global dark mode body styles and mesh gradient utility.

**IMPLEMENT:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 antialiased transition-colors duration-200;
  }
}

@layer utilities {
  .bg-mesh-gradient {
    background-color: #0f172a;
    background-image:
      radial-gradient(at 40% 20%, rgba(30, 64, 175, 0.4) 0px, transparent 50%),
      radial-gradient(at 80% 0%, rgba(139, 92, 246, 0.3) 0px, transparent 50%),
      radial-gradient(at 0% 50%, rgba(55, 48, 163, 0.3) 0px, transparent 50%),
      radial-gradient(at 80% 50%, rgba(79, 70, 229, 0.2) 0px, transparent 50%),
      radial-gradient(at 0% 100%, rgba(30, 58, 138, 0.3) 0px, transparent 50%),
      radial-gradient(at 80% 100%, rgba(91, 33, 182, 0.3) 0px, transparent 50%);
  }

  .bg-mesh-gradient-light {
    background-color: #f8fafc;
    background-image:
      radial-gradient(at 40% 20%, rgba(59, 130, 246, 0.08) 0px, transparent 50%),
      radial-gradient(at 80% 0%, rgba(139, 92, 246, 0.06) 0px, transparent 50%),
      radial-gradient(at 0% 50%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
      radial-gradient(at 80% 50%, rgba(79, 70, 229, 0.04) 0px, transparent 50%);
  }
}
```

**VALIDATE:** `cd frontend && npm run build`

---

### Task 3: UPDATE `frontend/src/components/layout/Layout.tsx`

Apply gradient mesh background with dark/light variants.

**IMPLEMENT:**
```typescript
import { Header } from './Header';
import { Footer } from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-mesh-gradient-light dark:bg-mesh-gradient transition-colors duration-200">
      <Header />
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        {children}
      </main>
      <Footer />
    </div>
  );
}
```

**VALIDATE:** `cd frontend && npm run dev` - visually verify gradient background

---

### Task 4: UPDATE `frontend/src/components/layout/Header.tsx`

Convert to glass morphism with dark mode support.

**IMPLEMENT:**
```typescript
import { FileText } from 'lucide-react';

export function Header() {
  return (
    <header className="backdrop-blur-xl bg-white/70 dark:bg-gray-900/70 border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg shadow-purple-500/25">
            <FileText className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Bluebeam PDF Map Converter
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Convert bid maps to deployment maps
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
```

**VALIDATE:** `cd frontend && npm run dev` - check header in light and dark mode

---

### Task 5: UPDATE `frontend/src/components/layout/Footer.tsx`

Add dark mode support.

**IMPLEMENT:**
```typescript
export function Footer() {
  return (
    <footer className="backdrop-blur-xl bg-white/70 dark:bg-gray-900/70 border-t border-gray-200/50 dark:border-gray-700/50 mt-auto">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
          Bluebeam PDF Map Converter v1.0.0
        </p>
      </div>
    </footer>
  );
}
```

**VALIDATE:** `cd frontend && npm run build`

---

### Task 6: UPDATE `frontend/src/components/ui/Card.tsx`

Add glass morphism effect and dark mode support.

**IMPLEMENT:**
```typescript
import { cn } from '../../lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn(
      'backdrop-blur-xl bg-white/80 dark:bg-gray-900/80',
      'rounded-2xl',
      'border border-white/50 dark:border-gray-700/50',
      'shadow-glass dark:shadow-glass-lg',
      'ring-1 ring-black/5 dark:ring-white/10',
      className
    )}>
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ children, className }: CardProps) {
  return (
    <div className={cn(
      'px-6 py-4 border-b border-gray-200/50 dark:border-gray-700/50',
      className
    )}>
      {children}
    </div>
  );
};

Card.Body = function CardBody({ children, className }: CardProps) {
  return (
    <div className={cn('px-6 py-4', className)}>
      {children}
    </div>
  );
};
```

**VALIDATE:** `cd frontend && npm run build`

---

### Task 7: UPDATE `frontend/src/components/ui/Button.tsx`

Add gradient primary variant and dark mode support.

**IMPLEMENT:**
```typescript
import { cn } from '../../lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export function Button({
  children,
  className,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled,
  ...props
}: ButtonProps) {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 focus:ring-purple-500 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40',
    secondary: 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 hover:bg-gray-200 dark:hover:bg-gray-700 focus:ring-gray-500 border border-gray-200 dark:border-gray-700',
    outline: 'border-2 border-purple-500 dark:border-purple-400 text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 focus:ring-purple-500',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={cn(baseClasses, variantClasses[variant], sizeClasses[size], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Processing...
        </>
      ) : (
        children
      )}
    </button>
  );
}
```

**VALIDATE:** `cd frontend && npm run build`

---

### Task 8: UPDATE `frontend/src/components/ui/Alert.tsx`

Add dark mode variants for all alert types.

**IMPLEMENT:**
```typescript
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';
import { cn } from '../../lib/utils';

interface AlertProps {
  variant: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  children: React.ReactNode;
  className?: string;
  onDismiss?: () => void;
}

const variantConfig = {
  success: {
    bg: 'bg-green-50/80 dark:bg-green-900/20',
    border: 'border-green-200/50 dark:border-green-700/50',
    text: 'text-green-800 dark:text-green-200',
    icon: CheckCircle,
    iconColor: 'text-green-500 dark:text-green-400',
  },
  error: {
    bg: 'bg-red-50/80 dark:bg-red-900/20',
    border: 'border-red-200/50 dark:border-red-700/50',
    text: 'text-red-800 dark:text-red-200',
    icon: XCircle,
    iconColor: 'text-red-500 dark:text-red-400',
  },
  warning: {
    bg: 'bg-yellow-50/80 dark:bg-yellow-900/20',
    border: 'border-yellow-200/50 dark:border-yellow-700/50',
    text: 'text-yellow-800 dark:text-yellow-200',
    icon: AlertCircle,
    iconColor: 'text-yellow-500 dark:text-yellow-400',
  },
  info: {
    bg: 'bg-blue-50/80 dark:bg-blue-900/20',
    border: 'border-blue-200/50 dark:border-blue-700/50',
    text: 'text-blue-800 dark:text-blue-200',
    icon: Info,
    iconColor: 'text-blue-500 dark:text-blue-400',
  },
};

export function Alert({ variant, title, children, className, onDismiss }: AlertProps) {
  const config = variantConfig[variant];
  const Icon = config.icon;

  return (
    <div
      role="alert"
      className={cn(
        'backdrop-blur-sm rounded-xl border p-4',
        config.bg,
        config.border,
        className
      )}
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <Icon className={cn('h-5 w-5', config.iconColor)} />
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={cn('text-sm font-medium', config.text)}>{title}</h3>
          )}
          <div className={cn('text-sm', config.text, title && 'mt-1')}>
            {children}
          </div>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <button
              onClick={onDismiss}
              className={cn(
                'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900',
                config.text,
                'hover:bg-white/50 dark:hover:bg-black/20'
              )}
            >
              <span className="sr-only">Dismiss</span>
              <X className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
```

**VALIDATE:** `cd frontend && npm run build`

---

### Task 9: UPDATE `frontend/src/components/ui/Spinner.tsx`

Update colors for dark mode compatibility.

**IMPLEMENT:**
```typescript
import { cn } from '../../lib/utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <svg
      className={cn('animate-spin text-purple-600 dark:text-purple-400', sizeClasses[size], className)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}
```

**VALIDATE:** `cd frontend && npm run build`

---

### Task 10: UPDATE `frontend/src/features/upload/components/DropZone.tsx`

Add glass effect and dark mode support.

**IMPLEMENT:** Update the className in the main drop zone div (around line 40-50):

Replace the existing conditional className with:
```typescript
<div
  {...getRootProps()}
  className={cn(
    'border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200',
    'backdrop-blur-sm',
    isDragActive && !isDragReject && 'border-purple-500 bg-purple-500/10 dark:bg-purple-500/20',
    isDragReject && 'border-red-500 bg-red-500/10 dark:bg-red-500/20',
    !isDragActive && !error && 'border-gray-300 dark:border-gray-600 hover:border-purple-400 dark:hover:border-purple-500 bg-white/50 dark:bg-gray-800/50 hover:bg-purple-50/50 dark:hover:bg-purple-900/20',
    error && 'border-red-300 dark:border-red-700 bg-red-50/50 dark:bg-red-900/20',
    disabled && 'opacity-50 cursor-not-allowed'
  )}
>
```

Also update icon container and text colors:
- Icon container: `bg-gray-100 dark:bg-gray-800` → `bg-purple-100 dark:bg-purple-900/50` when active
- Main text: Add `dark:text-gray-200`
- Secondary text: Add `dark:text-gray-400`
- Error text: Add `dark:text-red-400`

**PATTERN:** `frontend/src/features/upload/components/DropZone.tsx` lines 40-89
**VALIDATE:** `cd frontend && npm run build`

---

### Task 11: UPDATE `frontend/src/features/upload/components/FileInfo.tsx`

Add dark mode support to success card.

**IMPLEMENT:** Update the Card className and internal colors:

```typescript
<Card className="bg-green-50/80 dark:bg-green-900/20 border-green-200/50 dark:border-green-700/50">
```

Update icon box: `bg-green-100 dark:bg-green-900/50`
Update icon color: Already `text-green-600`, add `dark:text-green-400`
Update text colors: Add dark variants to `text-gray-900` → `dark:text-gray-100` and `text-gray-600` → `dark:text-gray-400`

**PATTERN:** `frontend/src/features/upload/components/FileInfo.tsx` lines 11-43
**VALIDATE:** `cd frontend && npm run build`

---

### Task 12: UPDATE `frontend/src/features/convert/components/ConversionPanel.tsx`

Add dark mode support.

**IMPLEMENT:** Update text and background colors:

- Header text: `text-gray-900` → `text-gray-900 dark:text-white`
- Result box: `bg-gray-50` → `bg-gray-100/50 dark:bg-gray-800/50`
- Stat labels: `text-gray-600` → `text-gray-600 dark:text-gray-400`
- Stat values: Ensure contrast with `dark:text-gray-200`

**PATTERN:** `frontend/src/features/convert/components/ConversionPanel.tsx` lines 29-79
**VALIDATE:** `cd frontend && npm run build`

---

### Task 13: UPDATE `frontend/src/features/convert/components/DirectionSelector.tsx`

Add dark mode for radio buttons and labels.

**IMPLEMENT:** Update the option styling:

Selected state:
- `border-primary-500 bg-primary-50` → `border-purple-500 dark:border-purple-400 bg-purple-50 dark:bg-purple-900/30`
- `ring-primary-500` → `ring-purple-500 dark:ring-purple-400`

Unselected state:
- `border-gray-200` → `border-gray-200 dark:border-gray-700`
- `hover:border-primary-300` → `hover:border-purple-300 dark:hover:border-purple-600`

Text colors:
- Label: Add `dark:text-gray-200`
- Description: Add `dark:text-gray-400`
- Disabled label: `text-gray-400 dark:text-gray-500`

**PATTERN:** `frontend/src/features/convert/components/DirectionSelector.tsx`
**VALIDATE:** `cd frontend && npm run build`

---

### Task 14: UPDATE `frontend/src/features/convert/components/ProgressDisplay.tsx`

Update step indicator colors for dark mode.

**IMPLEMENT:** Update the step circle colors:

- Complete: `bg-green-500` (keep as-is, works in both modes)
- Current: `bg-primary-500` → `bg-purple-500`
- Pending: `bg-gray-200` → `bg-gray-200 dark:bg-gray-700`

Connector lines:
- Complete: `bg-green-500` (keep as-is)
- Pending: `bg-gray-200` → `bg-gray-200 dark:bg-gray-700`

Labels:
- Complete: `text-green-600` → `text-green-600 dark:text-green-400`
- Current: `text-primary-600` → `text-purple-600 dark:text-purple-400`
- Pending: `text-gray-400` → `text-gray-400 dark:text-gray-500`

**PATTERN:** `frontend/src/features/convert/components/ProgressDisplay.tsx` lines 42-76
**VALIDATE:** `cd frontend && npm run build`

---

### Task 15: UPDATE `frontend/src/features/download/components/DownloadButton.tsx`

Add gradient styling to match new button design.

**IMPLEMENT:**
```typescript
import { Download } from 'lucide-react';

interface DownloadButtonProps {
  fileId: string;
  fileName: string;
}

export function DownloadButton({ fileId, fileName }: DownloadButtonProps) {
  const downloadUrl = `http://localhost:8000/api/download/${fileId}`;

  return (
    <a
      href={downloadUrl}
      download={fileName}
      className="inline-flex items-center justify-center w-full px-6 py-3 text-lg font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 focus:ring-purple-500 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40"
    >
      <Download className="h-5 w-5 mr-2" />
      Download {fileName}
    </a>
  );
}
```

**VALIDATE:** `cd frontend && npm run build`

---

### Task 16: UPDATE `frontend/src/App.tsx`

Update text colors for dark mode in main content area.

**IMPLEMENT:** Update these text classes:

- Main title: `text-gray-900` → `text-gray-900 dark:text-white`
- Description: `text-gray-600` → `text-gray-600 dark:text-gray-400`
- Card headers: `text-gray-900` → `text-gray-900 dark:text-white`

**PATTERN:** `frontend/src/App.tsx` lines 98-105 and throughout
**VALIDATE:** `cd frontend && npm run build`

---

## TESTING STRATEGY

### Visual Testing

1. **Light Mode Verification:**
   - Set system to light mode
   - Verify gradient background is subtle and visible
   - Check all cards have glass effect
   - Confirm text is readable
   - Test all interactive states (hover, focus, disabled)

2. **Dark Mode Verification:**
   - Set system to dark mode (or use DevTools)
   - Verify gradient background is rich and visible
   - Check glass effects work over dark gradient
   - Confirm text contrast is sufficient
   - Test all interactive states

3. **Component State Testing:**
   - Upload flow: idle → uploading → uploaded
   - Conversion flow: ready → converting → converted
   - Error states: upload error, conversion error
   - Success states: file info, conversion complete

### Browser Testing

Test in Chrome DevTools:
1. Open DevTools → Rendering tab
2. Scroll to "Emulate CSS media feature prefers-color-scheme"
3. Toggle between light and dark
4. Verify smooth transitions

### Accessibility Checklist

- [ ] Color contrast meets WCAG AA (4.5:1 for normal text)
- [ ] Focus rings visible in both modes
- [ ] No nested interactive elements
- [ ] All alerts have `role="alert"`

### Known Issues

- Pre-existing test failures: None in frontend
- Known limitations: None

---

## VALIDATION COMMANDS

### Level 1: Build Verification

```bash
cd frontend && npm run build
```
Expected: Build completes with no errors.

### Level 2: Type Checking

```bash
cd frontend && npx tsc --noEmit
```
Expected: No type errors.

### Level 3: Development Server

```bash
cd frontend && npm run dev
```
Expected: Dev server starts, app loads at http://localhost:5173

### Level 4: Manual Validation

1. Open http://localhost:5173 in browser
2. Toggle system dark mode preference
3. Verify:
   - Gradient background visible in both modes
   - Glass cards render with backdrop blur
   - All text is readable
   - Buttons show gradient effect
   - Progress indicators colored correctly
   - Alerts display properly in both modes

### Level 5: End-to-End Flow

1. Start backend: `cd backend && uv run uvicorn app.main:app --reload --port 8000`
2. Upload a test PDF
3. Run conversion
4. Download result
5. Verify entire flow works in both light and dark mode

---

## ACCEPTANCE CRITERIA

- [ ] Dark mode automatically activates based on system preference
- [ ] Gradient mesh background visible in both modes (subtle light, rich dark)
- [ ] All cards have glass morphism effect (backdrop blur, transparency)
- [ ] Buttons use blue-to-purple gradient
- [ ] All text is readable with proper contrast in both modes
- [ ] Focus rings work correctly in both modes
- [ ] Smooth transition when system theme changes
- [ ] No visual regressions in light mode
- [ ] Build completes with no errors
- [ ] Type checking passes
- [ ] Full upload → convert → download flow works

---

## COMPLETION CHECKLIST

- [ ] All 16 tasks completed in order
- [ ] Each task validation passed
- [ ] `npm run build` succeeds
- [ ] `npx tsc --noEmit` passes
- [ ] Visual verification in light mode
- [ ] Visual verification in dark mode
- [ ] End-to-end flow tested
- [ ] All acceptance criteria met

---

## NOTES

### Design Decisions

1. **`darkMode: 'media'` chosen over `'class'`** - Automatic system preference detection is simpler and aligns with user request. No manual toggle needed.

2. **Glass morphism over solid backgrounds** - Provides modern aesthetic while allowing gradient background to show through, creating depth.

3. **Blue-to-purple gradient** - Chosen for primary actions to create distinctive brand feel while maintaining professional appearance.

4. **Rounded corners increased to `rounded-xl` and `rounded-2xl`** - More modern, softer appearance consistent with current design trends.

5. **Shadow utilities (`shadow-glass`, `shadow-glow`)** - Custom shadows provide consistent depth without being overwhelming.

### Color Mapping Reference

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Body background | `bg-mesh-gradient-light` | `bg-mesh-gradient` |
| Card background | `bg-white/80` | `bg-gray-900/80` |
| Primary text | `text-gray-900` | `text-white` |
| Secondary text | `text-gray-600` | `text-gray-400` |
| Borders | `border-gray-200/50` | `border-gray-700/50` |
| Primary button | `from-blue-600 to-purple-600` | Same (gradient works in both) |
| Focus ring offset | Default (white) | `ring-offset-gray-900` |
