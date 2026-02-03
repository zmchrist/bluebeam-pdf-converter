# Feature: Custom Output Filename Input

The following plan should be complete, but validate documentation and codebase patterns before implementing.

Pay special attention to naming of existing utils, types, and models. Import from the right files.

## Feature Description

Add a text input field in the ConversionPanel that allows users to specify a custom name for the converted PDF file. The input appears before the "Convert to Deployment Map" button and is pre-populated with the default filename pattern (`{original}_deployment`). Users can edit this to any name they prefer, and the `.pdf` extension is automatically appended.

## User Story

As a project estimator
I want to specify a custom name for my converted deployment map
So that I can organize my files with meaningful names instead of auto-generated ones

## Problem Statement

Currently, converted files are automatically named `{original}_deployment.pdf`. Users have no control over the output filename and must rename files manually after download if they want different names.

## Solution Statement

Add an optional text input field that lets users specify a custom output filename. If left empty, the system uses the default naming convention. The backend sanitizes the filename for safety and ensures the `.pdf` extension is present.

## Feature Metadata

**Feature Type**: Enhancement
**Estimated Complexity**: Low
**Primary Systems Affected**: ConversionPanel (frontend), convert endpoint (backend), FileManager service
**Dependencies**: None (uses existing patterns)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - READ BEFORE IMPLEMENTING

| File | Lines | Why Read |
|------|-------|----------|
| `frontend/src/features/convert/components/ConversionPanel.tsx` | All | Component to modify - add input field |
| `frontend/src/features/convert/components/DirectionSelector.tsx` | All | Input styling patterns to mirror |
| `frontend/src/components/ui/Button.tsx` | All | Tailwind class patterns for disabled states |
| `frontend/src/types/index.ts` | 17-21 | ConversionRequest interface to update |
| `frontend/src/lib/api.ts` | 53-69 | convertPDF function to update |
| `frontend/src/features/convert/hooks/useConvert.ts` | All | Hook to update with new parameter |
| `frontend/src/App.tsx` | 56-76 | handleConvert callback to update |
| `backend/app/models/pdf_file.py` | 31-34 | ConversionRequest Pydantic model |
| `backend/app/routers/convert.py` | 29-33, 122-127 | Endpoint handler, store_converted call |
| `backend/app/services/file_manager.py` | 98-137, 209-217 | store_converted method, sanitization |

### New Files to Create

None - all changes are modifications to existing files.

### Patterns to Follow

**Tailwind Input Styling** (from DirectionSelector.tsx):
```tsx
className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600
           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
           focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500
           disabled:opacity-50 disabled:cursor-not-allowed
           transition-all duration-200"
```

**State Management** (from ConversionPanel.tsx):
```tsx
const [direction, setDirection] = useState<ConversionDirection>('bid_to_deployment');
```

**Pydantic Optional Fields** (from existing models):
```python
output_filename: str | None = None
```

**Filename Sanitization** (from file_manager.py:209-217):
```python
@staticmethod
def _sanitize_filename(name: str) -> str:
    safe_name = Path(name).name
    for char in ['/', '\\', '..', '\x00']:
        safe_name = safe_name.replace(char, '_')
    return safe_name
```

---

## IMPLEMENTATION PLAN

### Phase 1: Backend Model & Service Updates

Update the backend to accept and use an optional custom filename parameter.

**Tasks:**
- Add `output_filename` field to ConversionRequest model
- Update FileManager.store_converted() to accept custom filename
- Update convert endpoint to pass filename through

### Phase 2: Frontend Type & API Updates

Update TypeScript types and API client to support the new parameter.

**Tasks:**
- Add `output_filename` to ConversionRequest interface
- Update convertPDF() function signature
- Update useConvert hook

### Phase 3: UI Component Updates

Add the text input field to ConversionPanel and wire up the data flow.

**Tasks:**
- Add filename state to ConversionPanel
- Add text input with proper styling
- Update onConvert callback signature
- Update App.tsx handleConvert

### Phase 4: Testing & Validation

Verify the feature works end-to-end.

**Tasks:**
- Test with custom filename
- Test with empty filename (default behavior)
- Test filename sanitization

---

## STEP-BY-STEP TASKS

### Task 1: UPDATE `backend/app/models/pdf_file.py`

- **IMPLEMENT**: Add optional `output_filename` field to ConversionRequest
- **PATTERN**: Follow existing Pydantic model patterns in same file
- **IMPORTS**: None needed (already has BaseModel)

```python
class ConversionRequest(BaseModel):
    """Request model for PDF conversion endpoint."""

    direction: str  # "bid_to_deployment" or "deployment_to_bid"
    output_filename: str | None = None  # Optional custom output filename
```

- **VALIDATE**: `cd backend && uv run python -c "from app.models.pdf_file import ConversionRequest; print(ConversionRequest(direction='bid_to_deployment', output_filename='test.pdf'))"`

---

### Task 2: UPDATE `backend/app/services/file_manager.py`

- **IMPLEMENT**: Add `custom_filename` parameter to store_converted() method
- **PATTERN**: Use existing `_sanitize_filename()` method (line 209)
- **GOTCHA**: Ensure .pdf extension is added if not present

Update method signature (line 98-103):
```python
def store_converted(
    self,
    content: bytes,
    original_name: str,
    upload_id: str,
    custom_filename: str | None = None,
) -> FileMetadata:
```

Update filename logic (replace lines 117-119):
```python
# Create deployment filename
if custom_filename:
    # Use custom filename, ensure .pdf extension
    sanitized = self._sanitize_filename(custom_filename)
    if not sanitized.lower().endswith('.pdf'):
        sanitized = f"{sanitized}.pdf"
    converted_name = sanitized
else:
    # Default: add _deployment suffix
    base_name = Path(original_name).stem
    converted_name = f"{base_name}_deployment.pdf"
```

- **VALIDATE**: `cd backend && uv run pytest tests/test_file_manager.py -v`

---

### Task 3: UPDATE `backend/app/routers/convert.py`

- **IMPLEMENT**: Extract output_filename from request and pass to store_converted
- **PATTERN**: Follow existing request parameter extraction (line 60-62)

Update the store_converted call (around line 122-127):
```python
# 11. Store converted file
converted_content = output_path.read_bytes()
output_filename = request.output_filename if request else None
converted_metadata = file_manager.store_converted(
    converted_content,
    upload_metadata.original_name,
    upload_id,
    custom_filename=output_filename,
)
```

- **VALIDATE**: `cd backend && uv run pytest tests/test_api.py -v`

---

### Task 4: UPDATE `frontend/src/types/index.ts`

- **IMPLEMENT**: Add output_filename to ConversionRequest interface
- **PATTERN**: Follow existing optional field patterns

Update interface (lines 17-20):
```typescript
// Request body for POST /api/convert/{upload_id}
export interface ConversionRequest {
  direction: string;
  output_filename?: string;
}
```

- **VALIDATE**: `cd frontend && npx tsc --noEmit`

---

### Task 5: UPDATE `frontend/src/lib/api.ts`

- **IMPLEMENT**: Accept and pass outputFilename parameter to API
- **PATTERN**: Follow existing request body construction (line 57)

Update function signature and body (lines 53-69):
```typescript
/**
 * Convert an uploaded PDF from bid to deployment icons.
 */
export async function convertPDF(
  uploadId: string,
  direction: string = 'bid_to_deployment',
  outputFilename?: string
): Promise<ConversionResponse> {
  const request: ConversionRequest = {
    direction,
    ...(outputFilename && { output_filename: outputFilename }),
  };

  try {
    const response = await api.post<ConversionResponse>(
      `/api/convert/${uploadId}`,
      request,
      { timeout: 60000 }
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}
```

- **VALIDATE**: `cd frontend && npx tsc --noEmit`

---

### Task 6: UPDATE `frontend/src/features/convert/hooks/useConvert.ts`

- **IMPLEMENT**: Add outputFilename to ConvertParams interface
- **PATTERN**: Follow existing interface pattern

```typescript
import { useMutation } from '@tanstack/react-query';
import { convertPDF } from '../../../lib/api';
import type { ConversionResponse } from '../../../types';

interface ConvertParams {
  uploadId: string;
  direction: string;
  outputFilename?: string;
}

export function useConvert() {
  return useMutation<ConversionResponse, Error, ConvertParams>({
    mutationFn: ({ uploadId, direction, outputFilename }) =>
      convertPDF(uploadId, direction, outputFilename),
  });
}
```

- **VALIDATE**: `cd frontend && npx tsc --noEmit`

---

### Task 7: UPDATE `frontend/src/features/convert/components/ConversionPanel.tsx`

- **IMPLEMENT**: Add filename state, text input, and update callback
- **PATTERN**: Mirror DirectionSelector styling
- **IMPORTS**: Add `useEffect` to imports
- **GOTCHA**: Pre-populate with default name when uploadData changes

Update imports:
```typescript
import { useState, useEffect } from 'react';
```

Update props interface:
```typescript
interface ConversionPanelProps {
  uploadData: PDFUploadResponse;
  workflowStep: WorkflowStep;
  isConverting: boolean;
  conversionResult: ConversionResponse | null;
  onConvert: (direction: ConversionDirection, outputFilename: string) => void;
}
```

Add state after direction state:
```typescript
const [direction, setDirection] = useState<ConversionDirection>('bid_to_deployment');
const [outputFilename, setOutputFilename] = useState<string>('');

// Initialize filename when upload data changes
useEffect(() => {
  const baseName = uploadData.file_name.replace(/\.pdf$/i, '');
  setOutputFilename(`${baseName}_deployment`);
}, [uploadData.file_name]);
```

Add input field after DirectionSelector, before progress display:
```tsx
{/* Output filename input */}
<div className="space-y-2">
  <label
    htmlFor="output-filename"
    className="block text-sm font-medium text-gray-700 dark:text-gray-300"
  >
    Output Filename
  </label>
  <div className="flex items-center">
    <input
      id="output-filename"
      type="text"
      value={outputFilename}
      onChange={(e) => setOutputFilename(e.target.value)}
      disabled={isConverting || workflowStep === 'converted'}
      placeholder="Enter filename"
      className="flex-1 px-4 py-2 rounded-l-lg border border-gray-300 dark:border-gray-600
                 bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-200"
    />
    <span className="px-3 py-2 bg-gray-100 dark:bg-gray-700 border border-l-0 border-gray-300 dark:border-gray-600 rounded-r-lg text-gray-500 dark:text-gray-400 text-sm">
      .pdf
    </span>
  </div>
</div>
```

Update button onClick:
```tsx
<Button
  onClick={() => onConvert(direction, outputFilename)}
  isLoading={isConverting}
  className="w-full"
  size="lg"
>
  Convert to Deployment Map
</Button>
```

- **VALIDATE**: `cd frontend && npx tsc --noEmit && npm run build`

---

### Task 8: UPDATE `frontend/src/App.tsx`

- **IMPLEMENT**: Update handleConvert to accept and pass outputFilename
- **PATTERN**: Follow existing callback pattern

Update handleConvert callback (around line 56-76):
```typescript
// Handle conversion
const handleConvert = useCallback(
  async (direction: ConversionDirection, outputFilename: string) => {
    if (!uploadData) return;

    setError(null);
    setWorkflowStep('converting');

    try {
      const result = await convertMutation.mutateAsync({
        uploadId: uploadData.upload_id,
        direction,
        outputFilename: outputFilename || undefined,
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
```

- **VALIDATE**: `cd frontend && npx tsc --noEmit && npm run build`

---

## TESTING STRATEGY

### Unit Tests

Backend FileManager should be tested with custom filenames:
- Custom filename with .pdf extension
- Custom filename without .pdf extension (should add it)
- Empty/null filename (should use default)
- Filename with invalid characters (should sanitize)

### Integration Tests

Test the full API flow:
```bash
# Upload a file, then convert with custom filename
curl -X POST "http://localhost:8000/api/convert/{upload_id}" \
  -H "Content-Type: application/json" \
  -d '{"direction": "bid_to_deployment", "output_filename": "my_custom_name.pdf"}'
```

### Edge Cases

- Empty filename field → Uses default `{original}_deployment.pdf`
- Filename with special characters → Sanitized by backend
- Filename already ending in .pdf → No double extension
- Very long filename → Truncated or rejected (consider 255 char limit)

### Manual Validation

1. Start backend: `cd backend && uv run uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Upload a PDF file
4. Verify input shows default name `{filename}_deployment`
5. Modify the filename
6. Click Convert
7. Download and verify filename matches input

---

## VALIDATION COMMANDS

### Level 1: Syntax & Style

```bash
cd backend && uv run ruff check .
cd frontend && npx tsc --noEmit
```

### Level 2: Unit Tests

```bash
cd backend && uv run pytest tests/test_file_manager.py -v
cd backend && uv run pytest tests/test_api.py -v
```

### Level 3: Integration Tests

```bash
cd backend && uv run pytest -x --tb=short
```

### Level 4: Frontend Build

```bash
cd frontend && npm run build
```

### Level 5: Manual End-to-End

1. Run backend and frontend
2. Upload PDF
3. Verify input field appears with default name
4. Change name to "my_test_file"
5. Convert and download
6. Verify downloaded file is named "my_test_file.pdf"

---

## ACCEPTANCE CRITERIA

- [ ] Text input field appears in ConversionPanel before convert button
- [ ] Input is pre-populated with `{original}_deployment` on file upload
- [ ] Input is editable before conversion starts
- [ ] Input is disabled during conversion
- [ ] Empty input uses default filename behavior
- [ ] Custom filename appears in downloaded file
- [ ] Backend sanitizes dangerous characters
- [ ] `.pdf` extension is auto-appended if missing
- [ ] All existing tests continue to pass
- [ ] Frontend builds without TypeScript errors

---

## COMPLETION CHECKLIST

- [ ] All 8 tasks completed in order
- [ ] Each task validation passed
- [ ] Backend tests pass
- [ ] Frontend builds successfully
- [ ] Manual E2E test confirms feature works
- [ ] No regressions in existing functionality

---

## NOTES

**Design Decisions:**
- Input field shows `.pdf` suffix as static text (not editable) to prevent confusion
- Filename is sanitized on backend for security (not frontend) to prevent bypasses
- Empty filename uses default rather than showing error (per user preference)
- useEffect initializes default filename when uploadData changes to handle re-uploads

**Future Considerations:**
- Could add frontend validation with character limit warning
- Could show preview of final filename before conversion
- Could persist last-used filename pattern in localStorage
