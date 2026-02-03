# Feature: React Frontend Implementation

The following plan should be complete, but it's important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Build a React frontend for the Bluebeam PDF Map Converter that provides a simple 3-step workflow: upload PDF → convert → download. The frontend connects to the existing FastAPI backend API endpoints to enable users to convert bid map PDFs to deployment map PDFs through an intuitive web interface.

## User Story

As a project estimator
I want to upload a bid map PDF and download a converted deployment map PDF via a web interface
So that I can automate the conversion process without manual icon replacement in under 1 minute

## Problem Statement

The backend API is fully functional (Phase 4 Backend complete), but users have no way to interact with it except through direct API calls (curl, Swagger UI). A web-based UI is needed to make the tool accessible to non-technical users who need to convert venue map PDFs quickly and reliably.

## Solution Statement

Build a single-page React application with:
1. Drag-and-drop PDF upload with validation feedback
2. Conversion direction selector (bid→deployment only for MVP)
3. Real-time progress tracking during conversion
4. Download capability for converted PDFs
5. Comprehensive error handling with user-friendly messages

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: Frontend (new), API integration
**Dependencies**: Backend API (complete), React 18, Vite, TanStack Query, Tailwind CSS

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `backend/app/models/pdf_file.py` (lines 1-53) - Why: TypeScript interfaces must match these Pydantic models exactly
- `backend/app/routers/upload.py` (lines 1-144) - Why: Understand upload validation, error messages, response format
- `backend/app/routers/convert.py` (lines 1-164) - Why: Understand conversion flow, timing, response structure
- `backend/app/routers/download.py` (lines 1-35) - Why: Understand download endpoint behavior
- `backend/app/config.py` (lines 1-49) - Why: CORS origins, max file size settings
- `.claude/reference/react-frontend-best-practices.md` - Why: Project styling/patterns guide
- `.claude/PRD.md` (Section 6, 10, 12) - Why: UI requirements, API spec, acceptance criteria

### New Files to Create

```
frontend/
├── index.html                    # HTML entry point
├── package.json                  # Dependencies and scripts
├── vite.config.ts               # Vite configuration
├── tsconfig.json                # TypeScript configuration
├── tsconfig.node.json           # TypeScript config for Node
├── tailwind.config.js           # Tailwind CSS configuration
├── postcss.config.js            # PostCSS configuration
├── .env                         # Environment variables
├── src/
│   ├── main.tsx                 # React entry point
│   ├── App.tsx                  # Main application component
│   ├── index.css                # Global styles + Tailwind directives
│   ├── vite-env.d.ts            # Vite type declarations
│   ├── types/
│   │   └── index.ts             # TypeScript interfaces
│   ├── lib/
│   │   ├── api.ts               # Axios HTTP client
│   │   └── utils.ts             # Utility functions
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx       # Reusable button component
│   │   │   ├── Card.tsx         # Card container component
│   │   │   ├── Spinner.tsx      # Loading spinner
│   │   │   └── Alert.tsx        # Error/success alerts
│   │   └── layout/
│   │       ├── Layout.tsx       # Main layout wrapper
│   │       ├── Header.tsx       # App header
│   │       └── Footer.tsx       # App footer
│   ├── features/
│   │   ├── upload/
│   │   │   ├── components/
│   │   │   │   ├── DropZone.tsx # Drag-drop upload area
│   │   │   │   └── FileInfo.tsx # Uploaded file display
│   │   │   ├── hooks/
│   │   │   │   └── useUpload.ts # Upload mutation hook
│   │   │   └── index.ts         # Barrel exports
│   │   ├── convert/
│   │   │   ├── components/
│   │   │   │   ├── ConversionPanel.tsx    # Main conversion UI
│   │   │   │   ├── DirectionSelector.tsx  # Direction radio buttons
│   │   │   │   └── ProgressDisplay.tsx    # Progress steps display
│   │   │   ├── hooks/
│   │   │   │   └── useConvert.ts          # Conversion mutation hook
│   │   │   └── index.ts
│   │   └── download/
│   │       ├── components/
│   │       │   └── DownloadButton.tsx     # Download button
│   │       └── index.ts
│   └── hooks/
│       └── useHealthCheck.ts    # Health check hook
```

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [Vite Getting Started](https://vitejs.dev/guide/)
  - Specific section: React TypeScript setup
  - Why: Project scaffolding and configuration
- [TanStack Query Mutations](https://tanstack.com/query/latest/docs/framework/react/guides/mutations)
  - Specific section: useMutation for file uploads
  - Why: Handle upload/convert mutations with loading states
- [react-dropzone Documentation](https://react-dropzone.js.org/)
  - Specific section: Basic usage, accept prop
  - Why: Drag-and-drop PDF upload implementation
- [Tailwind CSS Installation](https://tailwindcss.com/docs/guides/vite)
  - Specific section: Vite setup
  - Why: Styling configuration

### Patterns to Follow

**TypeScript Interfaces (must match backend Pydantic models):**
```typescript
// From backend/app/models/pdf_file.py
interface PDFUploadResponse {
  upload_id: string;
  file_name: string;
  file_size: number;
  status: string;
  page_count: number;
  annotation_count: number;
  message: string;
}

interface ConversionRequest {
  direction: string; // "bid_to_deployment"
}

interface ConversionResponse {
  upload_id: string;
  file_id: string;
  status: string;
  original_file: string;
  converted_file: string;
  direction: string;
  annotations_processed: number;
  annotations_converted: number;
  annotations_skipped: number;
  skipped_subjects: string[];
  processing_time_ms: number;
  download_url: string;
  message: string;
}
```

**Error Response Pattern (from backend):**
```typescript
interface APIError {
  detail: string;
  error_code?: string;
}
```

**Naming Conventions:**
- Components: PascalCase (`DropZone.tsx`, `ConversionPanel.tsx`)
- Hooks: camelCase with `use` prefix (`useUpload.ts`, `useConvert.ts`)
- Types: PascalCase interfaces (`PDFUploadResponse`)
- API functions: camelCase (`uploadPDF`, `convertPDF`)
- CSS: Tailwind utility classes

**Component Pattern:**
```tsx
// Simple functional component with TypeScript
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
  className?: string;
}

export function Button({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  className = ''
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`base-classes ${variantClasses[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
```

**Hook Pattern (TanStack Query):**
```typescript
export function useUploadPDF() {
  return useMutation({
    mutationFn: uploadPDF,
    onError: (error: Error) => {
      // Handle error
    },
  });
}
```

---

## IMPLEMENTATION PLAN

### Phase 1: Project Scaffolding

Set up the React project with Vite, TypeScript, and Tailwind CSS.

**Tasks:**
- Create frontend directory structure
- Initialize npm project with package.json
- Configure Vite with React plugin
- Set up TypeScript configuration
- Configure Tailwind CSS and PostCSS
- Create environment variables for API URL

### Phase 2: Core Infrastructure

Build the foundational components and utilities.

**Tasks:**
- Create API client with axios
- Define TypeScript interfaces matching backend models
- Build reusable UI components (Button, Card, Spinner, Alert)
- Create layout components (Header, Footer, Layout)

### Phase 3: Upload Feature

Implement the PDF upload functionality.

**Tasks:**
- Build DropZone component with react-dropzone
- Create FileInfo component to display uploaded file metadata
- Implement useUpload hook with TanStack Query mutation
- Add client-side validation (file type, size)

### Phase 4: Conversion Feature

Implement the conversion workflow.

**Tasks:**
- Build DirectionSelector component (bid→deployment only)
- Create ProgressDisplay component with step indicators
- Build ConversionPanel to orchestrate the workflow
- Implement useConvert hook with mutation

### Phase 5: Download Feature

Implement the download capability.

**Tasks:**
- Build DownloadButton component
- Implement download trigger using file_id

### Phase 6: Main Application

Assemble all components into the main app.

**Tasks:**
- Build App.tsx with workflow state management
- Set up QueryClientProvider
- Implement "Convert Another" reset functionality
- Add comprehensive error handling

### Phase 7: Testing & Validation

Manual testing and validation.

**Tasks:**
- Test with BidMap.pdf upload and conversion
- Verify error handling for invalid files
- Test reset/retry functionality

---

## STEP-BY-STEP TASKS

IMPORTANT: Execute every task in order, top to bottom. Each task is atomic and independently testable.

### CREATE frontend/package.json

- **IMPLEMENT**: NPM package configuration with all dependencies
- **PATTERN**: Standard Vite + React + TypeScript setup
- **GOTCHA**: Use exact versions to ensure reproducibility
- **VALIDATE**: `cd frontend && npm install`

```json
{
  "name": "bluebeam-pdf-converter-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.0",
    "react-dropzone": "^14.2.3",
    "lucide-react": "^0.303.0",
    "clsx": "^2.1.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

### CREATE frontend/vite.config.ts

- **IMPLEMENT**: Vite configuration with React plugin and proxy for API
- **PATTERN**: Standard Vite React setup
- **GOTCHA**: Proxy to backend on port 8000 for development
- **VALIDATE**: `cd frontend && npm run dev` (after other configs)

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### CREATE frontend/tsconfig.json

- **IMPLEMENT**: TypeScript configuration for React
- **PATTERN**: Strict mode with React JSX support
- **VALIDATE**: No errors when running `npx tsc --noEmit`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### CREATE frontend/tsconfig.node.json

- **IMPLEMENT**: TypeScript config for Vite config file
- **VALIDATE**: Included by tsconfig.json references

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

### CREATE frontend/tailwind.config.js

- **IMPLEMENT**: Tailwind CSS configuration
- **PATTERN**: Standard Vite setup from Tailwind docs
- **GOTCHA**: Content paths must include all TSX files
- **VALIDATE**: Tailwind classes work in components

```javascript
/** @type {import('tailwindcss').Config} */
export default {
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
        },
      },
    },
  },
  plugins: [],
}
```

### CREATE frontend/postcss.config.js

- **IMPLEMENT**: PostCSS configuration for Tailwind
- **VALIDATE**: CSS processes correctly

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### CREATE frontend/index.html

- **IMPLEMENT**: HTML entry point
- **PATTERN**: Standard Vite React template
- **VALIDATE**: Page loads in browser

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Bluebeam PDF Map Converter</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### CREATE frontend/src/vite-env.d.ts

- **IMPLEMENT**: Vite TypeScript declarations
- **VALIDATE**: No TS errors referencing Vite types

```typescript
/// <reference types="vite/client" />
```

### CREATE frontend/src/index.css

- **IMPLEMENT**: Global styles with Tailwind directives
- **PATTERN**: Tailwind base/components/utilities
- **VALIDATE**: Styles apply correctly

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  @apply bg-gray-50 text-gray-900 antialiased;
}
```

### CREATE frontend/src/types/index.ts

- **IMPLEMENT**: TypeScript interfaces matching backend models
- **PATTERN**: Match `backend/app/models/pdf_file.py` exactly
- **GOTCHA**: Use string for UUID types, number for integers
- **VALIDATE**: `npx tsc --noEmit`

```typescript
/**
 * TypeScript interfaces matching backend Pydantic models.
 * See: backend/app/models/pdf_file.py
 */

// Response from POST /api/upload
export interface PDFUploadResponse {
  upload_id: string;
  file_name: string;
  file_size: number;
  status: string;
  page_count: number;
  annotation_count: number;
  message: string;
}

// Request body for POST /api/convert/{upload_id}
export interface ConversionRequest {
  direction: string;
}

// Response from POST /api/convert/{upload_id}
export interface ConversionResponse {
  upload_id: string;
  file_id: string;
  status: string;
  original_file: string;
  converted_file: string;
  direction: string;
  annotations_processed: number;
  annotations_converted: number;
  annotations_skipped: number;
  skipped_subjects: string[];
  processing_time_ms: number;
  download_url: string;
  message: string;
}

// Response from GET /health
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  version: string;
  timestamp: string;
  mapping_loaded: boolean;
  mapping_count: number;
  toolchest_bid_icons: number;
  toolchest_deployment_icons: number;
  error?: string;
}

// API error response format
export interface APIError {
  detail: string;
  error_code?: string;
}

// Workflow step for progress display
export type WorkflowStep =
  | 'idle'
  | 'uploading'
  | 'uploaded'
  | 'converting'
  | 'converted'
  | 'error';

// Direction options (MVP: only bid_to_deployment)
export type ConversionDirection = 'bid_to_deployment';
```

### CREATE frontend/src/lib/api.ts

- **IMPLEMENT**: Axios HTTP client with API functions
- **PATTERN**: Centralized API client
- **GOTCHA**: Upload uses FormData, convert uses JSON
- **VALIDATE**: Import and call functions without TS errors

```typescript
/**
 * API client for Bluebeam PDF Converter backend.
 */

import axios, { AxiosError } from 'axios';
import type {
  PDFUploadResponse,
  ConversionRequest,
  ConversionResponse,
  HealthCheckResponse,
  APIError
} from '../types';

// Base URL is proxied by Vite in development
const api = axios.create({
  baseURL: '',
  timeout: 120000, // 2 minutes for large file uploads
});

// Error handler to extract message from API response
function handleError(error: unknown): never {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<APIError>;
    const message = axiosError.response?.data?.detail || axiosError.message;
    throw new Error(message);
  }
  throw error;
}

/**
 * Upload a PDF file for conversion.
 */
export async function uploadPDF(file: File): Promise<PDFUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post<PDFUploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

/**
 * Convert an uploaded PDF from bid to deployment icons.
 */
export async function convertPDF(
  uploadId: string,
  direction: string = 'bid_to_deployment'
): Promise<ConversionResponse> {
  const request: ConversionRequest = { direction };

  try {
    const response = await api.post<ConversionResponse>(
      `/api/convert/${uploadId}`,
      request
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

/**
 * Get download URL for converted PDF.
 * Returns the full URL path for download.
 */
export function getDownloadUrl(fileId: string): string {
  return `/api/download/${fileId}`;
}

/**
 * Check backend health status.
 */
export async function checkHealth(): Promise<HealthCheckResponse> {
  try {
    const response = await api.get<HealthCheckResponse>('/health');
    return response.data;
  } catch (error) {
    handleError(error);
  }
}
```

### CREATE frontend/src/lib/utils.ts

- **IMPLEMENT**: Utility functions (format file size, etc.)
- **VALIDATE**: Functions work correctly

```typescript
/**
 * Utility functions for the frontend.
 */

import { clsx, type ClassValue } from 'clsx';

/**
 * Merge class names with clsx.
 */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

/**
 * Format file size in human-readable format.
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Format duration in milliseconds to human-readable format.
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

/**
 * Validate file is a PDF.
 */
export function isPDFFile(file: File): boolean {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
}

/**
 * Max file size in bytes (50MB).
 */
export const MAX_FILE_SIZE = 50 * 1024 * 1024;

/**
 * Validate file size is within limit.
 */
export function isFileSizeValid(file: File): boolean {
  return file.size <= MAX_FILE_SIZE;
}
```

### CREATE frontend/src/components/ui/Button.tsx

- **IMPLEMENT**: Reusable button component with variants
- **PATTERN**: Tailwind utility classes with variants
- **VALIDATE**: Renders with correct styles

```tsx
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
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 focus:ring-primary-500',
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
      {isLoading && (
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
      )}
      {children}
    </button>
  );
}
```

### CREATE frontend/src/components/ui/Card.tsx

- **IMPLEMENT**: Card container component
- **PATTERN**: Compound component pattern
- **VALIDATE**: Renders with header/body sections

```tsx
import { cn } from '../../lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn('bg-white rounded-xl shadow-sm border border-gray-200', className)}>
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ children, className }: CardProps) {
  return (
    <div className={cn('px-6 py-4 border-b border-gray-200', className)}>
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

### CREATE frontend/src/components/ui/Spinner.tsx

- **IMPLEMENT**: Loading spinner component
- **VALIDATE**: Animates correctly

```tsx
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
      className={cn('animate-spin text-primary-600', sizeClasses[size], className)}
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

### CREATE frontend/src/components/ui/Alert.tsx

- **IMPLEMENT**: Alert component for errors and success messages
- **PATTERN**: Variant-based styling
- **VALIDATE**: Displays correctly with different variants

```tsx
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';
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
    bg: 'bg-green-50',
    border: 'border-green-200',
    text: 'text-green-800',
    icon: CheckCircle,
    iconColor: 'text-green-400',
  },
  error: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-800',
    icon: XCircle,
    iconColor: 'text-red-400',
  },
  warning: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    text: 'text-yellow-800',
    icon: AlertCircle,
    iconColor: 'text-yellow-400',
  },
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-800',
    icon: Info,
    iconColor: 'text-blue-400',
  },
};

export function Alert({ variant, title, children, className, onDismiss }: AlertProps) {
  const config = variantConfig[variant];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        'rounded-lg border p-4',
        config.bg,
        config.border,
        className
      )}
      role="alert"
    >
      <div className="flex">
        <Icon className={cn('h-5 w-5 flex-shrink-0', config.iconColor)} />
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={cn('text-sm font-medium', config.text)}>{title}</h3>
          )}
          <div className={cn('text-sm', config.text, title && 'mt-1')}>
            {children}
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={cn('ml-auto -mx-1.5 -my-1.5 p-1.5 rounded-lg hover:bg-white/50', config.text)}
          >
            <XCircle className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
```

### CREATE frontend/src/components/layout/Header.tsx

- **IMPLEMENT**: Application header component
- **VALIDATE**: Displays app title

```tsx
import { FileText } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-100 rounded-lg">
            <FileText className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              Bluebeam PDF Map Converter
            </h1>
            <p className="text-sm text-gray-500">
              Convert bid maps to deployment maps
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
```

### CREATE frontend/src/components/layout/Footer.tsx

- **IMPLEMENT**: Application footer component
- **VALIDATE**: Displays correctly

```tsx
export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <p className="text-sm text-gray-500 text-center">
          Bluebeam PDF Map Converter v1.0.0
        </p>
      </div>
    </footer>
  );
}
```

### CREATE frontend/src/components/layout/Layout.tsx

- **IMPLEMENT**: Main layout wrapper
- **PATTERN**: Flex column with header/main/footer
- **VALIDATE**: Children render in main section

```tsx
import { Header } from './Header';
import { Footer } from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        {children}
      </main>
      <Footer />
    </div>
  );
}
```

### CREATE frontend/src/features/upload/components/DropZone.tsx

- **IMPLEMENT**: Drag-and-drop PDF upload zone
- **PATTERN**: react-dropzone with validation
- **GOTCHA**: Accept only PDFs, validate size client-side
- **VALIDATE**: File drop triggers onFileSelect callback

```tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText } from 'lucide-react';
import { cn } from '../../../lib/utils';
import { isPDFFile, isFileSizeValid, MAX_FILE_SIZE, formatFileSize } from '../../../lib/utils';

interface DropZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  error?: string | null;
}

export function DropZone({ onFileSelect, disabled = false, error }: DropZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        if (!isPDFFile(file)) {
          return; // Will be handled by onDropRejected
        }
        if (!isFileSizeValid(file)) {
          return; // Will be handled by onDropRejected
        }
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize: MAX_FILE_SIZE,
    maxFiles: 1,
    disabled,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all',
        isDragActive && !isDragReject && 'border-primary-500 bg-primary-50',
        isDragReject && 'border-red-500 bg-red-50',
        !isDragActive && !error && 'border-gray-300 hover:border-primary-400 hover:bg-gray-50',
        error && 'border-red-300 bg-red-50',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-4">
        <div
          className={cn(
            'p-4 rounded-full',
            isDragActive && !isDragReject && 'bg-primary-100',
            isDragReject && 'bg-red-100',
            !isDragActive && 'bg-gray-100'
          )}
        >
          {isDragReject ? (
            <FileText className="h-10 w-10 text-red-500" />
          ) : (
            <Upload
              className={cn(
                'h-10 w-10',
                isDragActive ? 'text-primary-600' : 'text-gray-400'
              )}
            />
          )}
        </div>
        <div>
          <p className="text-lg font-medium text-gray-700">
            {isDragActive
              ? isDragReject
                ? 'Invalid file type'
                : 'Drop your PDF here'
              : 'Drag & drop your bid map PDF'}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            or click to browse (max {formatFileSize(MAX_FILE_SIZE)})
          </p>
        </div>
        {error && (
          <p className="text-sm text-red-600 font-medium">{error}</p>
        )}
      </div>
    </div>
  );
}
```

### CREATE frontend/src/features/upload/components/FileInfo.tsx

- **IMPLEMENT**: Display uploaded file information
- **PATTERN**: Card with file metadata
- **VALIDATE**: Shows file name, size, page count, annotation count

```tsx
import { FileText, Check, Layers, MapPin } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { formatFileSize } from '../../../lib/utils';
import type { PDFUploadResponse } from '../../../types';

interface FileInfoProps {
  uploadData: PDFUploadResponse;
}

export function FileInfo({ uploadData }: FileInfoProps) {
  return (
    <Card className="bg-green-50 border-green-200">
      <Card.Body>
        <div className="flex items-start gap-4">
          <div className="p-3 bg-green-100 rounded-lg">
            <FileText className="h-8 w-8 text-green-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900 truncate">
                {uploadData.file_name}
              </h3>
              <Check className="h-5 w-5 text-green-600 flex-shrink-0" />
            </div>
            <div className="mt-2 flex flex-wrap gap-4 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <FileText className="h-4 w-4" />
                {formatFileSize(uploadData.file_size)}
              </span>
              <span className="flex items-center gap-1">
                <Layers className="h-4 w-4" />
                {uploadData.page_count} page{uploadData.page_count !== 1 ? 's' : ''}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {uploadData.annotation_count} annotations
              </span>
            </div>
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}
```

### CREATE frontend/src/features/upload/hooks/useUpload.ts

- **IMPLEMENT**: TanStack Query mutation hook for upload
- **PATTERN**: useMutation with error handling
- **VALIDATE**: Hook returns mutation state and mutate function

```typescript
import { useMutation } from '@tanstack/react-query';
import { uploadPDF } from '../../../lib/api';
import type { PDFUploadResponse } from '../../../types';

export function useUpload() {
  return useMutation<PDFUploadResponse, Error, File>({
    mutationFn: uploadPDF,
  });
}
```

### CREATE frontend/src/features/upload/index.ts

- **IMPLEMENT**: Barrel exports for upload feature
- **VALIDATE**: Exports work correctly

```typescript
export { DropZone } from './components/DropZone';
export { FileInfo } from './components/FileInfo';
export { useUpload } from './hooks/useUpload';
```

### CREATE frontend/src/features/convert/components/DirectionSelector.tsx

- **IMPLEMENT**: Radio button selector for conversion direction
- **GOTCHA**: MVP only supports bid_to_deployment
- **VALIDATE**: Shows selected state correctly

```tsx
import { ArrowRight } from 'lucide-react';
import { cn } from '../../../lib/utils';
import type { ConversionDirection } from '../../../types';

interface DirectionSelectorProps {
  value: ConversionDirection;
  onChange: (direction: ConversionDirection) => void;
  disabled?: boolean;
}

export function DirectionSelector({ value, onChange, disabled }: DirectionSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-gray-700">Conversion Direction</label>
      <div className="space-y-2">
        {/* Bid to Deployment - Enabled */}
        <label
          className={cn(
            'flex items-center gap-3 p-4 border rounded-lg cursor-pointer transition-all',
            value === 'bid_to_deployment'
              ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-500'
              : 'border-gray-200 hover:border-primary-300',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <input
            type="radio"
            name="direction"
            value="bid_to_deployment"
            checked={value === 'bid_to_deployment'}
            onChange={() => onChange('bid_to_deployment')}
            disabled={disabled}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500"
          />
          <div className="flex items-center gap-2">
            <span className="font-medium">Bid</span>
            <ArrowRight className="h-4 w-4 text-gray-400" />
            <span className="font-medium">Deployment</span>
          </div>
        </label>

        {/* Deployment to Bid - Disabled (Phase 2) */}
        <label
          className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg opacity-50 cursor-not-allowed"
          title="Coming in Phase 2"
        >
          <input
            type="radio"
            name="direction"
            value="deployment_to_bid"
            disabled
            className="h-4 w-4 text-gray-400"
          />
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-400">Deployment</span>
            <ArrowRight className="h-4 w-4 text-gray-300" />
            <span className="font-medium text-gray-400">Bid</span>
          </div>
          <span className="ml-auto text-xs text-gray-400">(Coming soon)</span>
        </label>
      </div>
    </div>
  );
}
```

### CREATE frontend/src/features/convert/components/ProgressDisplay.tsx

- **IMPLEMENT**: Progress steps display during conversion
- **PATTERN**: Step indicators with current state
- **VALIDATE**: Shows correct step highlighted

```tsx
import { Check, Loader2 } from 'lucide-react';
import { cn } from '../../../lib/utils';
import type { WorkflowStep } from '../../../types';

interface ProgressDisplayProps {
  currentStep: WorkflowStep;
}

const steps = [
  { key: 'uploading', label: 'Uploading PDF' },
  { key: 'uploaded', label: 'PDF Uploaded' },
  { key: 'converting', label: 'Converting Icons' },
  { key: 'converted', label: 'Conversion Complete' },
] as const;

function getStepStatus(
  stepKey: string,
  currentStep: WorkflowStep
): 'complete' | 'current' | 'pending' {
  const stepOrder = ['uploading', 'uploaded', 'converting', 'converted'];
  const currentIndex = stepOrder.indexOf(currentStep);
  const stepIndex = stepOrder.indexOf(stepKey);

  if (stepIndex < currentIndex) return 'complete';
  if (stepIndex === currentIndex) return 'current';
  return 'pending';
}

export function ProgressDisplay({ currentStep }: ProgressDisplayProps) {
  if (currentStep === 'idle' || currentStep === 'error') return null;

  return (
    <div className="py-4">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(step.key, currentStep);
          return (
            <div key={step.key} className="flex items-center">
              {/* Step indicator */}
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center transition-all',
                    status === 'complete' && 'bg-green-500',
                    status === 'current' && 'bg-primary-500',
                    status === 'pending' && 'bg-gray-200'
                  )}
                >
                  {status === 'complete' ? (
                    <Check className="h-5 w-5 text-white" />
                  ) : status === 'current' ? (
                    <Loader2 className="h-5 w-5 text-white animate-spin" />
                  ) : (
                    <span className="text-sm text-gray-500">{index + 1}</span>
                  )}
                </div>
                <span
                  className={cn(
                    'mt-2 text-xs font-medium text-center',
                    status === 'complete' && 'text-green-600',
                    status === 'current' && 'text-primary-600',
                    status === 'pending' && 'text-gray-400'
                  )}
                >
                  {step.label}
                </span>
              </div>
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    'flex-1 h-1 mx-2 rounded',
                    status === 'complete' ? 'bg-green-500' : 'bg-gray-200'
                  )}
                  style={{ minWidth: '40px' }}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

### CREATE frontend/src/features/convert/components/ConversionPanel.tsx

- **IMPLEMENT**: Main conversion UI panel
- **PATTERN**: Card with direction selector and convert button
- **VALIDATE**: Shows convert button, triggers conversion

```tsx
import { useState } from 'react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { DirectionSelector } from './DirectionSelector';
import { ProgressDisplay } from './ProgressDisplay';
import type { ConversionDirection, WorkflowStep, PDFUploadResponse, ConversionResponse } from '../../../types';

interface ConversionPanelProps {
  uploadData: PDFUploadResponse;
  workflowStep: WorkflowStep;
  isConverting: boolean;
  conversionResult: ConversionResponse | null;
  onConvert: (direction: ConversionDirection) => void;
}

export function ConversionPanel({
  uploadData,
  workflowStep,
  isConverting,
  conversionResult,
  onConvert,
}: ConversionPanelProps) {
  const [direction, setDirection] = useState<ConversionDirection>('bid_to_deployment');

  const showConvertButton = workflowStep === 'uploaded';
  const showProgress = workflowStep === 'converting' || workflowStep === 'converted';

  return (
    <Card>
      <Card.Header>
        <h2 className="text-lg font-semibold text-gray-900">Convert PDF</h2>
      </Card.Header>
      <Card.Body className="space-y-6">
        {/* Direction selector */}
        <DirectionSelector
          value={direction}
          onChange={setDirection}
          disabled={isConverting}
        />

        {/* Progress display */}
        {showProgress && <ProgressDisplay currentStep={workflowStep} />}

        {/* Conversion result summary */}
        {conversionResult && (
          <div className="p-4 bg-gray-50 rounded-lg space-y-2">
            <p className="text-sm text-gray-600">
              <span className="font-medium">Converted:</span>{' '}
              {conversionResult.annotations_converted} of {conversionResult.annotations_processed} annotations
            </p>
            {conversionResult.annotations_skipped > 0 && (
              <p className="text-sm text-gray-500">
                <span className="font-medium">Skipped:</span>{' '}
                {conversionResult.annotations_skipped} (no mapping)
              </p>
            )}
            <p className="text-sm text-gray-500">
              <span className="font-medium">Processing time:</span>{' '}
              {(conversionResult.processing_time_ms / 1000).toFixed(1)}s
            </p>
          </div>
        )}

        {/* Convert button */}
        {showConvertButton && (
          <Button
            onClick={() => onConvert(direction)}
            isLoading={isConverting}
            className="w-full"
            size="lg"
          >
            Convert to Deployment Map
          </Button>
        )}
      </Card.Body>
    </Card>
  );
}
```

### CREATE frontend/src/features/convert/hooks/useConvert.ts

- **IMPLEMENT**: TanStack Query mutation hook for conversion
- **PATTERN**: useMutation with parameters
- **VALIDATE**: Hook returns mutation state

```typescript
import { useMutation } from '@tanstack/react-query';
import { convertPDF } from '../../../lib/api';
import type { ConversionResponse } from '../../../types';

interface ConvertParams {
  uploadId: string;
  direction: string;
}

export function useConvert() {
  return useMutation<ConversionResponse, Error, ConvertParams>({
    mutationFn: ({ uploadId, direction }) => convertPDF(uploadId, direction),
  });
}
```

### CREATE frontend/src/features/convert/index.ts

- **IMPLEMENT**: Barrel exports for convert feature
- **VALIDATE**: Exports work correctly

```typescript
export { ConversionPanel } from './components/ConversionPanel';
export { DirectionSelector } from './components/DirectionSelector';
export { ProgressDisplay } from './components/ProgressDisplay';
export { useConvert } from './hooks/useConvert';
```

### CREATE frontend/src/features/download/components/DownloadButton.tsx

- **IMPLEMENT**: Download button for converted PDF
- **PATTERN**: Anchor tag styled as button
- **GOTCHA**: Use download attribute for proper filename
- **VALIDATE**: Clicking triggers file download

```tsx
import { Download } from 'lucide-react';
import { Button } from '../../../components/ui/Button';
import { getDownloadUrl } from '../../../lib/api';

interface DownloadButtonProps {
  fileId: string;
  fileName: string;
}

export function DownloadButton({ fileId, fileName }: DownloadButtonProps) {
  const downloadUrl = getDownloadUrl(fileId);

  return (
    <a href={downloadUrl} download={fileName}>
      <Button size="lg" className="w-full">
        <Download className="h-5 w-5 mr-2" />
        Download {fileName}
      </Button>
    </a>
  );
}
```

### CREATE frontend/src/features/download/index.ts

- **IMPLEMENT**: Barrel exports for download feature
- **VALIDATE**: Exports work correctly

```typescript
export { DownloadButton } from './components/DownloadButton';
```

### CREATE frontend/src/App.tsx

- **IMPLEMENT**: Main application component with workflow state
- **PATTERN**: Single-page workflow with state management
- **GOTCHA**: Reset all state on "Convert Another"
- **VALIDATE**: Full workflow works end-to-end

```tsx
import { useState, useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Card } from './components/ui/Card';
import { Button } from './components/ui/Button';
import { Alert } from './components/ui/Alert';
import { DropZone, FileInfo, useUpload } from './features/upload';
import { ConversionPanel, useConvert } from './features/convert';
import { DownloadButton } from './features/download';
import type { WorkflowStep, PDFUploadResponse, ConversionResponse, ConversionDirection } from './types';
import { RefreshCw } from 'lucide-react';

// Create QueryClient outside component to avoid recreation
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
    mutations: {
      retry: 0,
    },
  },
});

function PDFConverter() {
  // Workflow state
  const [workflowStep, setWorkflowStep] = useState<WorkflowStep>('idle');
  const [uploadData, setUploadData] = useState<PDFUploadResponse | null>(null);
  const [conversionResult, setConversionResult] = useState<ConversionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Mutations
  const uploadMutation = useUpload();
  const convertMutation = useConvert();

  // Handle file selection
  const handleFileSelect = useCallback(
    async (file: File) => {
      setError(null);
      setWorkflowStep('uploading');

      try {
        const result = await uploadMutation.mutateAsync(file);
        setUploadData(result);
        setWorkflowStep('uploaded');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Upload failed');
        setWorkflowStep('error');
      }
    },
    [uploadMutation]
  );

  // Handle conversion
  const handleConvert = useCallback(
    async (direction: ConversionDirection) => {
      if (!uploadData) return;

      setError(null);
      setWorkflowStep('converting');

      try {
        const result = await convertMutation.mutateAsync({
          uploadId: uploadData.upload_id,
          direction,
        });
        setConversionResult(result);
        setWorkflowStep('converted');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Conversion failed');
        setWorkflowStep('error');
      }
    },
    [uploadData, convertMutation]
  );

  // Reset to start new conversion
  const handleReset = useCallback(() => {
    setWorkflowStep('idle');
    setUploadData(null);
    setConversionResult(null);
    setError(null);
    uploadMutation.reset();
    convertMutation.reset();
  }, [uploadMutation, convertMutation]);

  const showDropZone = workflowStep === 'idle' || workflowStep === 'error';
  const showFileInfo = uploadData && workflowStep !== 'idle';
  const showConversionPanel = uploadData && (workflowStep === 'uploaded' || workflowStep === 'converting' || workflowStep === 'converted');
  const showDownload = conversionResult && workflowStep === 'converted';
  const showResetButton = workflowStep === 'converted' || workflowStep === 'error';

  return (
    <Layout>
      <div className="space-y-6">
        {/* Title and description */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">
            Convert Your Bid Map
          </h2>
          <p className="text-gray-600 mt-2">
            Upload a PDF bid map to convert all bid icons to deployment icons
          </p>
        </div>

        {/* Error display */}
        {error && (
          <Alert variant="error" title="Error" onDismiss={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Success message */}
        {workflowStep === 'converted' && conversionResult && (
          <Alert variant="success" title="Conversion Complete!">
            Successfully converted {conversionResult.annotations_converted} annotations.
            {conversionResult.annotations_skipped > 0 && (
              <> ({conversionResult.annotations_skipped} skipped due to missing mappings)</>
            )}
          </Alert>
        )}

        {/* Step 1: Upload */}
        {showDropZone && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold text-gray-900">
                Step 1: Upload PDF
              </h3>
            </Card.Header>
            <Card.Body>
              <DropZone
                onFileSelect={handleFileSelect}
                disabled={uploadMutation.isPending}
                error={workflowStep === 'error' ? error : null}
              />
            </Card.Body>
          </Card>
        )}

        {/* File info display */}
        {showFileInfo && <FileInfo uploadData={uploadData} />}

        {/* Step 2: Convert */}
        {showConversionPanel && (
          <ConversionPanel
            uploadData={uploadData}
            workflowStep={workflowStep}
            isConverting={convertMutation.isPending}
            conversionResult={conversionResult}
            onConvert={handleConvert}
          />
        )}

        {/* Step 3: Download */}
        {showDownload && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold text-gray-900">
                Step 3: Download
              </h3>
            </Card.Header>
            <Card.Body>
              <DownloadButton
                fileId={conversionResult.file_id}
                fileName={conversionResult.converted_file}
              />
            </Card.Body>
          </Card>
        )}

        {/* Reset button */}
        {showResetButton && (
          <div className="flex justify-center">
            <Button variant="outline" onClick={handleReset}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Convert Another PDF
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <PDFConverter />
    </QueryClientProvider>
  );
}
```

### CREATE frontend/src/main.tsx

- **IMPLEMENT**: React entry point
- **PATTERN**: Standard Vite React entry
- **VALIDATE**: App renders in browser

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### RUN npm install and verify build

- **VALIDATE**: `cd frontend && npm install && npm run build`

### RUN development server and test

- **VALIDATE**:
  1. Start backend: `cd backend && uv run uvicorn app.main:app --reload --port 8000`
  2. Start frontend: `cd frontend && npm run dev`
  3. Open http://localhost:5173
  4. Upload `samples/maps/BidMap.pdf`
  5. Click "Convert to Deployment Map"
  6. Download converted PDF

---

## TESTING STRATEGY

### Manual Testing (MVP - No Automated Frontend Tests)

**Scope:** Verify all user workflows work correctly

1. **Upload Test**: Drag PDF onto drop zone, verify file info displays
2. **Invalid File Test**: Try uploading non-PDF, verify error message
3. **Large File Test**: Try uploading file > 50MB, verify error message
4. **Conversion Test**: Convert BidMap.pdf, verify success message
5. **Download Test**: Download converted PDF, verify it opens correctly
6. **Reset Test**: Click "Convert Another PDF", verify workflow resets
7. **Error Recovery Test**: Trigger error, dismiss alert, retry

### Edge Cases

- Upload file with spaces in name
- Upload while backend is down (network error)
- Rapid clicking on convert button (should be disabled)
- Refresh page during conversion (state lost - expected)

---

## VALIDATION COMMANDS

### Level 1: Syntax & Build

```bash
cd frontend
npm install
npm run build
```

### Level 2: TypeScript Check

```bash
cd frontend
npx tsc --noEmit
```

### Level 3: Development Server

```bash
# Terminal 1: Start backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend && npm run dev
```

### Level 4: Manual Validation

1. Open http://localhost:5173
2. Verify page loads with header "Bluebeam PDF Map Converter"
3. Drag `samples/maps/BidMap.pdf` onto drop zone
4. Verify file info shows: ~4.3 MB, 1 page, 400+ annotations
5. Click "Convert to Deployment Map"
6. Wait for conversion (should take ~1-2 seconds)
7. Verify success message shows converted count
8. Click download button
9. Open downloaded PDF and verify icons changed
10. Click "Convert Another PDF" and verify workflow resets

---

## ACCEPTANCE CRITERIA

- [ ] Frontend builds without errors (`npm run build`)
- [ ] TypeScript compiles without errors (`npx tsc --noEmit`)
- [ ] Drop zone accepts PDF files only
- [ ] Drop zone rejects files > 50MB with error message
- [ ] Upload shows file metadata (name, size, pages, annotations)
- [ ] Direction selector defaults to "Bid → Deployment"
- [ ] "Deployment → Bid" option is disabled with "Coming soon" label
- [ ] Convert button triggers API call and shows loading state
- [ ] Progress display shows steps during conversion
- [ ] Success message shows conversion statistics
- [ ] Download button triggers file download
- [ ] Downloaded PDF has correct filename (*_deployment.pdf)
- [ ] Error messages are user-friendly and actionable
- [ ] "Convert Another PDF" resets entire workflow
- [ ] UI is responsive on 1920x1080 and 1366x768 displays
- [ ] BidMap.pdf converts successfully end-to-end

---

## COMPLETION CHECKLIST

- [ ] All configuration files created (package.json, vite.config.ts, etc.)
- [ ] All TypeScript types defined matching backend models
- [ ] All UI components created and styled with Tailwind
- [ ] Upload feature implemented with react-dropzone
- [ ] Convert feature implemented with TanStack Query
- [ ] Download feature implemented
- [ ] App.tsx orchestrates full workflow
- [ ] Build succeeds without errors
- [ ] TypeScript compiles without errors
- [ ] Manual testing confirms all workflows work
- [ ] BidMap.pdf converts successfully via UI

---

## NOTES

### Design Decisions

1. **No routing**: Single-page workflow doesn't need React Router for MVP
2. **No state management library**: useState + TanStack Query sufficient for MVP
3. **No automated tests**: Manual testing for MVP, add Vitest later
4. **Vite proxy**: Development proxy to backend avoids CORS issues

### API Contract Summary

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/upload` | POST | `FormData { file }` | `PDFUploadResponse` |
| `/api/convert/{upload_id}` | POST | `{ direction }` | `ConversionResponse` |
| `/api/download/{file_id}` | GET | - | Binary PDF |
| `/health` | GET | - | `HealthCheckResponse` |

### Error Messages (from backend)

- "File is not a PDF. Please upload a PDF venue map."
- "PDF file too large (max 50MB). Please reduce file size."
- "Multi-page PDFs not yet supported. Please upload a single-page venue map."
- "No icon markup annotations found in PDF. Please verify you uploaded a marked-up bid map."
- "Upload session not found or expired."
- "Conversion failed: {reason}"

### Performance Notes

- Upload/conversion can take 1-5 seconds for large PDFs
- Set axios timeout to 120 seconds for safety
- Progress display provides feedback during wait

### Future Enhancements

- Add Vitest for unit testing
- Add progress percentage from backend (WebSocket)
- Add drag-drop preview before upload
- Add conversion history with localStorage
