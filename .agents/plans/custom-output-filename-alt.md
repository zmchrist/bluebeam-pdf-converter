# Plan: Add Custom Output Filename Input

## Summary
Add a text input field before the "Convert to Deployment Map" button that allows users to specify a custom name for the converted PDF file.

## Current Flow
1. User uploads PDF (e.g., `BidMap.pdf`)
2. User clicks "Convert to Deployment Map"
3. Backend auto-generates filename: `{original}_deployment.pdf` → `BidMap_deployment.pdf`

## New Flow
1. User uploads PDF (e.g., `BidMap.pdf`)
2. Text input pre-populated with `BidMap_deployment` (editable)
3. User can modify the name
4. User clicks "Convert to Deployment Map"
5. File is saved with user's custom name + `.pdf` extension

---

## Files to Modify

### Frontend (4 files)

**1. `frontend/src/types/index.ts`**
- Add `output_filename?: string` to `ConversionRequest` interface

**2. `frontend/src/lib/api.ts`**
- Update `convertPDF()` to accept and pass `outputFilename` parameter

**3. `frontend/src/features/convert/hooks/useConvert.ts`**
- Update `ConvertParams` interface to include `outputFilename`
- Pass it through to `convertPDF()`

**4. `frontend/src/features/convert/components/ConversionPanel.tsx`**
- Add state for `outputFilename` (default: `{uploadedFilename}_deployment`)
- Add text input field with label "Output filename"
- Update `onConvert` call to include the filename
- Update `ConversionPanelProps.onConvert` signature

**5. `frontend/src/App.tsx`**
- Update `handleConvert` to accept and pass `outputFilename`

### Backend (3 files)

**6. `backend/app/models/pdf_file.py`**
- Add `output_filename: str | None = None` to `ConversionRequest`

**7. `backend/app/routers/convert.py`**
- Extract `output_filename` from request
- Pass it to `file_manager.store_converted()`

**8. `backend/app/services/file_manager.py`**
- Update `store_converted()` to accept optional `custom_filename` parameter
- Use custom filename if provided, otherwise default to `{base}_deployment.pdf`

---

## Implementation Details

### Frontend Input Component
```tsx
{/* Output filename input */}
<div className="space-y-2">
  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
    Output Filename
  </label>
  <div className="flex items-center">
    <input
      type="text"
      value={outputFilename}
      onChange={(e) => setOutputFilename(e.target.value)}
      className="flex-1 px-3 py-2 border rounded-l-md ..."
      disabled={isConverting}
    />
    <span className="px-3 py-2 bg-gray-100 border border-l-0 rounded-r-md">.pdf</span>
  </div>
</div>
```

### Default Filename Logic
When `uploadData` changes, set default:
```tsx
useEffect(() => {
  const baseName = uploadData.file_name.replace(/\.pdf$/i, '');
  setOutputFilename(`${baseName}_deployment`);
}, [uploadData.file_name]);
```

### Backend Validation
- Sanitize filename (remove invalid characters)
- Ensure `.pdf` extension is added if not present
- Max length check (255 characters)

---

## Verification Steps
1. Upload a PDF file
2. Verify text input appears with default name `{original}_deployment`
3. Edit the filename
4. Click Convert
5. Verify downloaded file has the custom name
6. Test edge cases: empty name (should use default), special characters

---

## Edge Cases to Handle
- **Empty filename → use default** `{original}_deployment.pdf` (user confirmed)
- Filename with `.pdf` already → don't double-add extension
- Invalid characters (/, \, etc.) → sanitize on backend
