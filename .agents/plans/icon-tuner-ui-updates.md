# Icon Tuner UI Updates

## Context

Follow-up to the Apply to All implementation. Five changes: (1) extend "Apply to All" to gear image, brand text, and model text sections in PropertiesPanel, (2) remove the non-functional reference overlay feature, (3) remove "mod"/"new" badges from icon list, (4) remove the Fiber category tab, (5) remove the search bar from icon selector.

## 1. Extend Apply to All — Backend

### `backend/app/models/tuner.py`
- Expand `field_group` literal: `Literal["circle", "id_box", "gear_image", "brand_text", "model_text"]`
- Add fields for the new groups:
  - `img_scale_ratio`, `img_x_offset`, `img_y_offset` (gear_image)
  - `brand_text`, `brand_font_size`, `brand_x_offset`, `brand_y_offset`, `text_color` (brand_text)
  - `model_font_size`, `model_x_offset`, `model_y_offset`, `model_uppercase`, `model_text_override` (model_text)

### `backend/app/routers/tuner.py`
- Add `elif` branches in the endpoint for `gear_image`, `brand_text`, `model_text` field groups, each extracting only their relevant fields via `model_dump(include=...)`

## 2. Extend Apply to All — Frontend

### `frontend/src/types/tuner.ts`
- Add new optional fields to `ApplyToAllRequest` interface matching backend additions
- Expand `field_group` union: `'circle' | 'id_box' | 'gear_image' | 'brand_text' | 'model_text'`

### `frontend/src/features/tuner/components/PropertiesPanel.tsx`
- Add `onApplyToAll?: (fieldGroup: 'gear_image' | 'brand_text' | 'model_text') => void` prop
- Add "Apply to All" button (Copy icon) in the header area for the active section, same pattern as FrameProperties

### `frontend/src/features/tuner/pages/IconTunerPage.tsx`
- Update `applyFieldGroup` state type to include all 5 field groups
- Update `handleConfirmApply` to build request fields for gear_image, brand_text, model_text
- Pass `onApplyToAll={handleOpenApplyModal}` to `<PropertiesPanel>`

### `frontend/src/features/tuner/components/ApplyToAllModal.tsx`
- Add labels for `gear_image`, `brand_text`, `model_text` to `FIELD_GROUP_LABELS`

## 3. Remove Reference Feature

### `frontend/src/features/tuner/components/Toolbar.tsx`
- Remove `showReference` and `onToggleReference` props
- Remove the Ref toggle button (lines 133-145)
- Remove `Eye`, `EyeOff` from lucide imports

### `frontend/src/features/tuner/pages/IconTunerPage.tsx`
- Remove `showReference` from `canvasState` initial state
- Remove `showReference` and `onToggleReference` props passed to `<Toolbar>`

### `frontend/src/features/tuner/components/CanvasEditor.tsx`
- Remove `referenceImage` state (currently always null, unused)
- Stop passing it to `useCanvasRenderer`

### `frontend/src/features/tuner/hooks/useCanvasRenderer.ts`
- Remove `referenceImage` parameter and the conditional draw block

### `frontend/src/types/tuner.ts`
- Remove `showReference` from `CanvasState` interface

## 4. Remove "mod" Badge from Icon List

### `frontend/src/features/tuner/components/IconSelector.tsx`
- Delete the `{icon.source !== 'python' && ...}` span (lines 89-93)

## 5. Remove Fiber Category Tab

### `frontend/src/features/tuner/components/IconSelector.tsx`
- Remove `'Fiber'` from `ALL_CATEGORIES` array

### `frontend/src/features/tuner/components/Toolbar.tsx`
- Remove `'Fiber'` from the `categories` array in the new icon dialog

## 6. Remove Search Bar

### `frontend/src/features/tuner/components/IconSelector.tsx`
- Remove `search` state and `Search` import
- Remove search filter from `filtered` useMemo
- Remove the search input div (lines 42-52)
- Simplify layout — category tabs become the only top row element

## File Summary

| File | Changes |
|------|---------|
| `backend/app/models/tuner.py` | Expand field_group literal + add fields |
| `backend/app/routers/tuner.py` | Add 3 elif branches for new field groups |
| `frontend/src/types/tuner.ts` | Expand ApplyToAllRequest, remove showReference from CanvasState |
| `frontend/src/features/tuner/components/PropertiesPanel.tsx` | Add onApplyToAll prop + buttons |
| `frontend/src/features/tuner/components/ApplyToAllModal.tsx` | Add 3 field group labels |
| `frontend/src/features/tuner/pages/IconTunerPage.tsx` | Wire new field groups, remove reference props |
| `frontend/src/features/tuner/components/Toolbar.tsx` | Remove Ref button + props, remove Fiber category |
| `frontend/src/features/tuner/components/IconSelector.tsx` | Remove search, mod badge, Fiber tab |
| `frontend/src/features/tuner/components/CanvasEditor.tsx` | Remove referenceImage state |
| `frontend/src/features/tuner/hooks/useCanvasRenderer.ts` | Remove referenceImage param |

## Verification

1. `cd backend && uv run ruff check app/routers/tuner.py app/models/tuner.py`
2. `cd backend && uv run pytest`
3. `cd frontend && npx tsc --noEmit`
4. Manual: select icon, click Apply to All on any section, verify modal shows all 5 field group labels
5. Confirm: no search bar, no "mod" badges, no Fiber tab, no Ref button
